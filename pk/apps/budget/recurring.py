# encoding: utf-8
"""
Recurring payment detection heuristics. This module identifies likely recurring
charges directly from transaction history without storing separate profile tables.

High-level flow:
1. Pull recent debit transactions for a user (lookback window).
2. Normalize each payee into a grouping key via scrub_payee().
3. For each payee group, run analyze_group() which rejects the group if:
   - span of dates is less than 70 days
   - cadence ratio is below 0.4 (monthly: 21-38 days, yearly: 358-372 days)
   - amounts ping-pong up/down with less than 60% flat changes
   - amount variability (MAD/median) exceeds 0.8
4. If the full group fails, retry with subgroups split by amount band
   (split_trxs_by_amount) to handle merchants with multiple price tiers.
5. Filter out inactive items unless include_inactive is set.
6. Return items sorted by cadence and name, with total monthly/yearly cost.
"""
import datetime, logging, statistics
from collections import defaultdict
from decimal import Decimal
from . import utils as butils
from .models import Transaction
log = logging.getLogger(__name__)


class RecurringDetector:
    MIN_CHARGE = Decimal('5.00')
    # COMMENT_TAGS = {'sub', 'subscription', 'recurring', 'renewal', 'autopay'}
    # RECURRING_CATEGORY_WORDS = {'subscription', 'subscriptions', 'software, games', 'software'}
    # BILL_CATEGORY_WORDS = {'loan', 'loans', 'mortgage', 'transfers', 'ignored', 'utilities', 'insurance', 'taxes', 'medical'}
    # BILL_PAYEE_WORDS = {'pymt', 'payment', 'loan', 'mortgage', 'cardmember', 'autopay', 'ach', 'taxpymt'}
    # RECURRING_PAYEE_WORDS = {'subscription', 'subscrip', 'premium', 'plus', 'membership', 'member', 'dues', 'stream'}
    # AGGREGATOR_TOKENS = {'google', 'apple', 'amazon', 'paypal', 'sq', 'amz'}
    CADENCE_RANGES = {'monthly':(21,38), 'yearly':(358,372)}
    ACTIVE_DAYS_BY_CADENCE = {'monthly':62, 'yearly':548}

    @classmethod
    def detect(cls, user, lookback_days=913, include_inactive=False):
        """Detect likely recurring payments directly from transactions without profile tables."""
        mindate = datetime.date.today() - datetime.timedelta(days=lookback_days)
        trxs = Transaction.objects.filter(user=user, amount__lt=cls.MIN_CHARGE, date__gte=mindate)
        trxs = trxs.select_related('account', 'category').order_by('date', 'id')
        # Group transactions by payee key {<scrubbed_payee>: [trx, ...]}
        # Only keep groups with at least 2 transactions
        groups = defaultdict(list)
        for trx in trxs:
            name = butils.scrub_payee(trx.payee)
            if len(name) < 3: continue
            groups[name].append(trx)
        groups = {name:trxs for name,trxs in groups.items() if len(trxs) >= 2}
        log.debug(f'Analyzing {len(groups)} groups for recurring transactions')
        # Detect recurring patterns within each group and assign confidence scores
        items = []
        for name, trxs in groups.items():
            # Check the item without including the amount
            if item := cls.analyze_group(name, trxs):
                items.append(item)
                continue
            # If we include Price in the grouping, can we detect a pattern?
            for subgroup in cls.split_trxs_by_amount(trxs):
                item = cls.analyze_group(name, subgroup)
                if item:
                    item['name'] = f"{item['name']} ({item['last_amount']})"
                    log.debug(f' + Amount-cluster fallback: {item["name"]}')
                    items.append(item)
        # Filter, Sort and Return items
        items = items if include_inactive else [item for item in items if item['is_active']]
        items = sorted(items, key=lambda item: (item['cadence'], item['name']))
        return {'count':len(items), 'items':items}

    @classmethod
    def analyze_group(cls, name, trxs):
        """ Compute cadence, confidence and cost estimates for one recurring payee group. """
        trxs = sorted(trxs, key=lambda trx: trx.date)
        # Check span days >= 70
        if span_days := (trxs[-1].date - trxs[0].date).days < 70:
            log.debug(f' - Span days {span_days} < 70: {name}')
            return None
        # Check cadence ratio >= 0.4
        cadence, cadence_ratio = cls.get_cadence_ratio(trxs)
        if cadence_ratio < 0.40:
            log.debug(f' - Cadence ratio {cadence_ratio:.2} < 0.4: {name}')
            return None
        # Check amounts do not ping-pong up/down
        amounts = [abs(Decimal(trx.amount)) for trx in trxs]
        amtdiffs = [amounts[i] - amounts[i-1] for i in range(1, len(amounts))]
        amtsame = len([1 for x in amtdiffs if x == 0])
        amtchange = len([1 for x in amtdiffs if x != 0])
        pctsame = amtsame / amtchange if amtchange else 1
        amtdirs = set([1 if diff > 0 else -1 if diff < 0 else 0 for diff in amtdiffs])
        if (1 in amtdirs and -1 in amtdirs) and (pctsame < 0.6):
            log.debug(f' - Amounts ping pong up/down {list(amtdirs)}: {name}')
            return None
        # Check amount variablity is not too high relative to median (MAD/median <= 0.9)
        if variability := cls.amount_variability(amounts) > 0.8:
            log.debug(f' - Amount variability {variability:.2} too high: {name}')
            return None
        # Collect metrics
        daysago = (datetime.date.today() - trxs[-1].date).days
        return {
            'name': name,
            'cadence': cadence,
            'count': len(trxs),
            'average': round(sum(amounts) / len(amounts), 2),
            'last_amount': round(amounts[-1], 2),
            'last_date': trxs[-1].date,
            'first_amount': round(amounts[-1], 2),
            'first_date': trxs[0].date,
            'accounts': sorted({trx.account.name for trx in trxs}),
            'categories': sorted({trx.category.name for trx in trxs if trx.category}),
            'is_active': cls.ACTIVE_DAYS_BY_CADENCE[cadence] >= daysago,
        }

    @classmethod
    def get_intervals(cls, trxs):
        """ Return list of day intervals between adjacent dates. """
        values = []
        for i in range(1, len(trxs)):
            delta = (trxs[i].date - trxs[i-1].date).days
            if delta > 0:
                values.append(delta)
        return values

    @classmethod
    def get_cadence_ratio(cls, trxs):
        """ Pick the cadence with best interval fit ratio. """
        scores = {}
        intervals = cls.get_intervals(trxs)
        for cadence, (mindays, maxdays) in cls.CADENCE_RANGES.items():
            matches = [d for d in intervals if d >= mindays and d <= maxdays]
            scores[cadence] = len(matches) / max(len(intervals), 1)
        cadence = max(scores.keys(), key=lambda item: scores[item])
        return cadence, scores[cadence]

    @classmethod
    def amount_variability(cls, amounts):
        """ Robust variability using MAD / median for amount drift tolerance. """
        median = Decimal(str(statistics.median([float(amount) for amount in amounts])))
        if median <= 0: return 1.0
        deviations = [abs(float(amount - median)) for amount in amounts]
        mad = statistics.median(deviations) if deviations else 0
        return float(mad / float(median))

    @classmethod
    def split_trxs_by_amount(cls, trxs):
        """ Split a merchant group by amount bands to handle multi-plan merchants. """
        subgroups = []
        for trx in sorted(trxs, key=lambda item: abs(Decimal(item.amount))):
            amount = abs(Decimal(trx.amount))
            for subgroup in subgroups:
                center = subgroup['center']
                tolerance = max(Decimal('1.50'), center * Decimal('0.18'))
                if abs(amount - center) <= tolerance:
                    subgroup['trxs'].append(trx)
                    values = [Decimal(item.amount) for item in subgroup['trxs']]
                    subgroup['center'] = Decimal(str(sum(values) / len(values)))
                    break
            else:
                subgroups.append({'center':amount, 'trxs':[trx]})
        return [subgroup['trxs'] for subgroup in subgroups if len(subgroup['trxs']) >= 2]

    # def analyze_group(cls, name, trxs):
    #     ...snip...
    #     occurrence_score = min(20.0, (len(trxs) / 18.0) * 10 + (span_days / 365.0) * 10)
    #     cadence_score = min(45.0, cadence_ratio * 45.0)
    #     amount_score = max(0.0, 20.0 * (1 - min(variability, 0.9) / 0.9))
    #     signal_score, reasons = cls.signal_adjustments(trxs, name)
    #     if cadence == 'yearly' and len(trxs) <= 3:
    #         signal_score += 6
    #         reasons.append('Sparse yearly cadence boost')
    #     kind, kind_score = cls.classify_kind(trxs, name, median, cadence)
    #     confidence = max(0, min(100, round(cadence_score + occurrence_score + amount_score + signal_score)))
    #     monthly_cost, yearly_cost = cls.estimate_cost(cadence, median, intervals)
    #     accounts = sorted({trx.account.name for trx in trxs})
    #     categories = sorted({trx.category.name for trx in trxs if trx.category})
    #     reasons = [f'{cadence.capitalize()} interval match {(cadence_ratio * 100):.0f}%'] + reasons
    #     days_since_last = (datetime.date.today() - trxs[-1].date).days
    #     stale_days = cls.STALE_DAYS_BY_CADENCE.get(cadence, 548)
    #     return {
    #         'name': name,
    #         'confidence': confidence,
    #         'kind': kind,
    #         'kind_score': kind_score,
    #         'cadence': cadence,
    #         'count': len(trxs),
    #         'first_date': trxs[0].date,
    #         'last_date': trxs[-1].date,
    #         'days_since_last': days_since_last,
    #         'is_stale': days_since_last > stale_days,
    #         # 'median': round(median, 2),
    #         'monthly_cost': round(monthly_cost, 2),
    #         'yearly_cost': round(yearly_cost, 2),
    #         'amount_variability': round(variability, 3),
    #         'accounts': accounts,
    #         'category_names': categories,
    #         'reasons': reasons[:4],
    #     }

    # @classmethod
    # def signal_adjustments(cls, trxs, key):
    #     """ Return score adjustments and human-readable reasons from soft signals. """
    #     score = 0.0
    #     reasons = []
    #     categories = {trx.category.name.lower() for trx in trxs if trx.category and trx.category.name}
    #     comments = ' '.join([(trx.comment or '').lower() for trx in trxs])
    #     if any([word in categories for word in cls.RECURRING_CATEGORY_WORDS]):
    #         score += 10
    #         reasons.append('Recurring category boost')
    #     if any([word in comments for word in cls.COMMENT_TAGS]):
    #         score += 8
    #         reasons.append('Comment tag boost')
    #     if any([word in categories for word in cls.BILL_CATEGORY_WORDS]):
    #         score -= 16
    #         reasons.append('Bill-like category penalty')
    #     key_tokens = set(key.split())
    #     if len(key_tokens & cls.BILL_PAYEE_WORDS) > 0:
    #         score -= 12
    #         reasons.append('Bill/payment keyword penalty')
    #     return score, reasons

    # @classmethod
    # def classify_kind(cls, trxs, key, median_amount, cadence):
    #     """Classify recurring groups as recurring-like or recurring bill-like."""
    #     score = 0
    #     categories = {trx.category.name.lower() for trx in trxs if trx.category and trx.category.name}
    #     comments = ' '.join([(trx.comment or '').lower() for trx in trxs])
    #     key_tokens = set(key.split())
    #     non_aggregator_tokens = [token for token in key_tokens if token not in cls.AGGREGATOR_TOKENS]
    #     if any([word in categories for word in cls.RECURRING_CATEGORY_WORDS]):
    #         score += 2
    #     if any([word in comments for word in cls.COMMENT_TAGS]):
    #         score += 1
    #     if len([word for word in cls.RECURRING_PAYEE_WORDS if word in key]) > 0:
    #         score += 1
    #     if cadence in {'monthly', 'yearly'}:
    #         score += 1
    #     if median_amount <= 80:
    #         score += 1
    #     if len(non_aggregator_tokens) >= 1:
    #         score += 1
    #     if cadence == 'yearly' and len(trxs) <= 3 and len(non_aggregator_tokens) >= 1:
    #         score += 1
    #     if any([word in categories for word in cls.BILL_CATEGORY_WORDS]):
    #         score -= 2
    #     if len(key_tokens & cls.BILL_PAYEE_WORDS) > 0:
    #         score -= 1
    #     if median_amount >= 150 and score <= 0:
    #         score -= 1
    #     kind = 'recurring' if score >= 3 else 'recurring_bill'
    #     return kind, score

    # @classmethod
    # def estimate_cost(cls, cadence, median_amount, intervals):
    #     """Convert detected cadence and amount into monthly/yearly estimates."""
    #     if cadence == 'monthly':
    #         monthly = median_amount
    #         yearly = median_amount * Decimal(12)
    #         return monthly, yearly
    #     if cadence == 'yearly':
    #         monthly = median_amount / Decimal(12)
    #         yearly = median_amount
    #         return monthly, yearly
    #     if cadence == 'quarterly':
    #         monthly = median_amount / Decimal(3)
    #         yearly = median_amount * Decimal(4)
    #         return monthly, yearly
    #     avg_interval = statistics.mean(intervals) if len(intervals) else 30
    #     monthly = median_amount * Decimal(30.4375 / max(avg_interval, 1))
    #     yearly = monthly * Decimal(12)
    #     return monthly, yearly
