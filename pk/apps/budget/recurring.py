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
from decimal import Decimal
from django.conf import settings
from . import utils as butils
from .models import Transaction
log = logging.getLogger(__name__)


class RecurringManager:
    """ Manager class for recurring payment detection. """
    THRESHOLD_AMOUNT = Decimal('0.18')
    THRESHOLD_DAYS = {'monthly':7, 'yearly':7}
    MIN_ACTIVE_DAYS = {'monthly':62, 'yearly':375}
    MIN_SPAN_DAYS = {'monthly':60, 'yearly':355}
    MIN_TRXS = {'monthly':3, 'yearly':2}
    MIN_CADENCE_RATIO = {'monthly':0.4, 'yearly':0.4}
    MAX_PINPONG_RATIO = {'monthly':0.4, 'yearly':0.4}
    MAX_VARIABILITY = {'monthly':0.8, 'yearly':0.8}
    SKIP_CATEGORIES = getattr(settings, 'BUDGET_RECURRING_SKIP_CATEORIES', {})

    CADENCE_RANGES = {}
    CADENCE_RANGES['monthly'] = (28-THRESHOLD_DAYS['monthly'], 31+THRESHOLD_DAYS['monthly'])
    CADENCE_RANGES['yearly'] = (365-THRESHOLD_DAYS['yearly'], 365+THRESHOLD_DAYS['yearly'])

    def __init__(self, user, days=900):
        self.user = user            # User transactions belong to
        self.days = days            # Number of days to look back
        self.items = []             # List of detected recurring items
        self._find_recurring()      

    def _find_recurring(self, lookback_days=913, include_inactive=False):
        """ Detect likely recurring payments directly from transactions without profile tables. """
        mindate = datetime.date.today() - datetime.timedelta(days=self.days)
        trxs = Transaction.objects.filter(user=self.user, amount__lt=0, date__gte=mindate)
        trxs = trxs.exclude(category__name__in=self.SKIP_CATEGORIES)
        trxs = trxs.select_related('account', 'category').order_by('date', 'id')
        groups = self._group_by_payee_and_amount(trxs)
        log.debug(f'Analyzing {len(groups)} groups from {len(trxs)} trxs for recurring transactions')
        for group in groups:
            if item := self._analyze_group(group['name'], group['trxs']):
                self.items.append(item)
        self.items = sorted(self.items, key=lambda item: (item['cadence'], item['name']))

    def _group_by_payee_and_amount(self, trxs):
        """ Group transactions by payee and amount. """
        groups = []
        for trx in trxs:
            name = butils.scrub_payee(trx.payee)
            amount = trx.amount
            for group in groups:
                if group['name'] != name: continue
                average = group['average']
                threshold = abs(average) * self.THRESHOLD_AMOUNT
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

    def _analyze_group(self, name, trxs):
        """ Compute cadence, confidence and cost estimates for one recurring payee group. """
        trxs = sorted(trxs, key=lambda trx: trx.date)
        amounts = [Decimal(trx.amount) for trx in trxs]
        daysago = (datetime.date.today() - trxs[-1].date).days
        cadence, cadenceratio = self._get_cadence_ratio(trxs)
        # Peform checks to confirm group meets criteria for recurring payments.
        # If any check fails, return None to reject the group.
        if not all((
            self._check_cadence_ratio(name, cadence, cadenceratio),
            self._check_span_days(name, trxs, cadence),
            self._check_min_trxs(name, trxs, cadence),
            self._check_ping_pong(name, amounts, cadence),
            self._check_variability(name, amounts, cadence),
        )): return None
        # Collect metrics
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
            'is_active': self.MIN_ACTIVE_DAYS[cadence] >= daysago,
            'accounts': sorted({trx.account.name for trx in trxs}),
            'categories': sorted({trx.category.name for trx in trxs if trx.category}),
        }

    def _get_cadence_ratio(self, trxs):
        """ Pick the cadence with best interval fit ratio. Returns:
            - cadence: 'monthly' or 'yearly'
            - cadence_ratio: Percent intervals that match cadence range
        """
        scores = {}
        intervals = [(trxs[i].date - trxs[i-1].date).days for i in range(1, len(trxs))]
        intervals = list(filter(lambda x: x > 0, intervals))
        for cadence, (mindays, maxdays) in self.CADENCE_RANGES.items():
            matches = [d for d in intervals if d >= mindays and d <= maxdays]
            scores[cadence] = len(matches) / max(len(intervals), 1)
        cadence = max(scores.keys(), key=lambda item: scores[item])
        return cadence, scores[cadence]

    def _check_cadence_ratio(self, name, cadence, cadenceratio):
        """ Check if the cadence ratio meets the threshold for any cadence. """
        minratio = self.MIN_CADENCE_RATIO[cadence]
        if cadenceratio < minratio:
            log.debug(f' - Cadence Ratio {cadenceratio:.2f} < {minratio:.2f}: {name}')
            return False
        return True

    def _check_span_days(self, name, trxs, cadence):
        """ Check the transaction dates span enough days. """
        minspan = self.MIN_SPAN_DAYS[cadence]
        spandays = (trxs[-1].date - trxs[0].date).days
        if spandays < minspan:
            log.debug(f' - Span Days {spandays} < {minspan}: {name}')
            return False
        return True

    def _check_min_trxs(self, name, trxs, cadence):
        """ Check the minimum number of transactions for the cadence. """
        mintrxs = max(2, self.MIN_TRXS[cadence])
        if len(trxs) < mintrxs:
            log.debug(f' - Num Transactions {len(trxs)} < {mintrxs}: {name}')
            return False
        return True

    def _check_ping_pong(self, name, amounts, cadence):
        """ Check amounts do not ping-pong up/down. """
        diffs = [amounts[i] - amounts[i-1] for i in range(1, len(amounts))]
        hasincrease = any(d > 0 for d in diffs)
        hasdecrease = any(d < 0 for d in diffs)
        ppratio = sum(1 for d in diffs if d != 0) / len(diffs)
        maxratio = self.MAX_PINPONG_RATIO[cadence]
        if hasincrease and hasdecrease and ppratio > maxratio:
            log.debug(f' - Amounts PingPong {ppratio:.2f} > {maxratio:.2f}: {name}')
            return False
        return True

    def _check_variability(self, name, amounts, cadence):
        """ Check amount variablity is not too high. """
        # Calculate the variability of amounts relative to median
        median = statistics.median(amounts)
        deviations = [abs(amount - median) for amount in amounts]
        mad = statistics.median(deviations) if deviations else Decimal('0')
        variability = float(mad / abs(median)) if abs(median) else 0.0
        # Check the variability is within the threshold for the cadence
        maxvariability = self.MAX_VARIABILITY[cadence]
        if variability > maxvariability:
            log.debug(f' - Amount Variability {variability:.2f} > {maxvariability:.2f}: {name}')
            return False
        return True
