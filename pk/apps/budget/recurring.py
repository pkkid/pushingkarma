# encoding: utf-8
"""
Recurring payment detection heuristics. This module identifies likely recurring
charges directly from transaction history without storing separate profile tables.

High-level flow:
1. Pull recent debit transactions for a user (lookback window).
2. Normalize each payee into a grouping key via scrub_payee().
3. For each payee group, run _analyze_group() which rejects the group if:
   - span of dates is less than 70 days
   - cadence ratio is below 0.4 (monthly: 21-38 days, yearly: 358-372 days)
   - amounts ping-pong up/down with less than 60% flat changes
   - amount variability (MAD/median) exceeds 0.8
4. If the full group fails, retry with subgroups split by amount band
   (_split_trxs_by_amount) to handle merchants with multiple price tiers.
5. Filter out inactive items unless include_inactive is set.
6. Return items sorted by cadence and name, with total monthly/yearly cost.
"""
import datetime, logging, statistics
from django.conf import settings
from decimal import Decimal
from . import utils as butils
from .models import Transaction
log = logging.getLogger(__name__)

# Cadence Ranges
# Interval ranges for each cadence, allowing for some fuzziness
CADENCE_RANGES = {'monthly':(
    28 - settings.BUDGET_RECURRING_THRESHOLD_DAYS['monthly'],   # monthly mindays
    31 + settings.BUDGET_RECURRING_THRESHOLD_DAYS['monthly']    # monthly maxdays
),'yearly':(
    365 - settings.BUDGET_RECURRING_THRESHOLD_DAYS['yearly'],   # yearly mindays
    365 + settings.BUDGET_RECURRING_THRESHOLD_DAYS['yearly']    # yearly maxdays
)}


def find_recurring_transactions(user, lookback_days=913, include_inactive=False):
    """ Detect likely recurring payments directly from transactions without profile tables. """
    mindate = datetime.date.today() - datetime.timedelta(days=lookback_days)
    trxs = Transaction.objects.filter(user=user, amount__lt=0, date__gte=mindate)
    trxs = trxs.select_related('account', 'category').order_by('date', 'id')
    groups = _group_by_payee_and_amount(trxs)
    log.debug(f'Analyzing {len(groups)} groups from {len(trxs)} trxs for recurring transactions')
    items = []
    for group in groups:
        if item := _analyze_group(group['name'], group['trxs']):
            items.append(item)
    items = items if include_inactive else [item for item in items if item['is_active']]
    items = sorted(items, key=lambda item: (item['cadence'], item['name']))
    return {'count':len(items), 'items':items}


def _group_by_payee_and_amount(trxs):
    """ Group transactions by payee and amount. """
    groups = []
    for trx in trxs:
        name = butils.scrub_payee(trx.payee)
        amount = trx.amount
        for group in groups:
            if group['name'] != name: continue
            average = group['average']
            threshold = abs(average) * settings.BUDGET_RECURRING_AMOUNT_THRESHOLD
            if amount-threshold <= average <= amount+threshold:
                values = [Decimal(trx.amount) for trx in group['trxs']]
                average = Decimal(str(sum(values) / len(values)))
                group['trxs'].append(trx)
                group['average'] = average
                break
        else:
            groups.append({'name':name, 'trxs':[trx], 'average':amount})
    # Only keep groups with at least 2 transactions
    return [g for g in groups if len(g['trxs']) >= 2]


def _analyze_group(name, trxs):
    """ Compute cadence, confidence and cost estimates for one recurring payee group. """
    trxs = sorted(trxs, key=lambda trx: trx.date)
    # Cadence Ratio
    # Check if the cadence ratio meets the threshold for any cadence
    cadence, cadence_ratio = _get_cadence_ratio(trxs)
    if cadence_ratio < 0.40:
        log.debug(f' - Cadence Ratio {cadence_ratio:.2f} < 0.4: {name}')
        return None
    # Span Days
    # Check the transaction dates span enough days
    minspan = settings.BUDGET_RECURRING_MIN_SPAN_DAYS[cadence]
    spandays = (trxs[-1].date - trxs[0].date).days
    if spandays < minspan:
        log.debug(f' - Span Days {spandays} < {minspan}: {name}')
        return None
    # Count Transactions
    # Check the mininmum number of transactions exist
    mintrxs = settings.BUDGET_RECURRING_MIN_TRXS[cadence]
    if len(trxs) < mintrxs:
        log.debug(f' - Num Transactions {len(trxs)} < {mintrxs}: {name}')
    # Amount Ping Pong
    # Check amounts do not ping-pong up/down
    amounts = [Decimal(trx.amount) for trx in trxs]
    amtdiffs = [amounts[i] - amounts[i-1] for i in range(1, len(amounts))]
    amtsame = len([1 for x in amtdiffs if x == 0])
    amtchange = len([1 for x in amtdiffs if x != 0])
    pctsame = amtsame / amtchange if amtchange else 1
    amtdirs = set([1 if diff > 0 else -1 if diff < 0 else 0 for diff in amtdiffs])
    if (1 in amtdirs and -1 in amtdirs) and (pctsame < 0.6):
        log.debug(f' - Amounts PingPong {list(amtdirs)}: {name}')
        return None
    # Amount Variability
    # Check amount variablity is not too high
    _amounts = [abs(amt) for amt in amounts]
    variability = _amount_variability(_amounts)
    if variability > 0.8:
        log.debug(f' - Amount Variability {variability} too high: {name}')
        return None
    # Collect metrics
    daysago = (datetime.date.today() - trxs[-1].date).days
    return {
        'name': name,
        'cadence': cadence,
        'average': round(sum(amounts) / len(amounts), 2),
        'count': len(trxs),
        'first_amount': round(amounts[-1], 2),
        'first_date': trxs[0].date,
        'last_amount': round(amounts[-1], 2),
        'last_date': trxs[-1].date,
        'max_amount': round(max(amounts), 2),
        'min_amount': round(min(amounts), 2),
        'accounts': sorted({trx.account.name for trx in trxs}),
        'categories': sorted({trx.category.name for trx in trxs if trx.category}),
        'is_active': settings.BUDGET_RECURRING_ACTIVE_THRESHOLD_DAYS[cadence] >= daysago,
    }

def _get_cadence_ratio(trxs):
    """ Pick the cadence with best interval fit ratio. Returns:
        - cadence: 'monthly' or 'yearly'
        - cadence_ratio: Percent intervals that match cadence range
    """
    scores = {}
    intervals = [(trxs[i].date - trxs[i-1].date).days for i in range(1, len(trxs))]
    intervals = list(filter(lambda x: x > 0, intervals))
    for cadence, (mindays, maxdays) in CADENCE_RANGES.items():
        matches = [d for d in intervals if d >= mindays and d <= maxdays]
        scores[cadence] = len(matches) / max(len(intervals), 1)
    cadence = max(scores.keys(), key=lambda item: scores[item])
    return cadence, scores[cadence]


def _amount_variability(amounts):
    """ Returns the variability of amounts relative to median (MAD/median),
        where MAD is the median absolute deviation.
    """
    median = Decimal(str(statistics.median([float(amount) for amount in amounts])))
    if median <= 0: return 1.0
    deviations = [abs(float(amount - median)) for amount in amounts]
    mad = statistics.median(deviations) if deviations else 0
    return float(mad / float(median))



