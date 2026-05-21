# encoding: utf-8
"""
Recurring payment detection heuristics. This module identifies likely recurring
charges directly from transaction history without storing separate profile tables.

High-level flow:
1. Pull recent debit transactions for a user (lookback window).
2. Normalize each payee into a grouping key (remove noisy/company suffix tokens).
3. For each payee group, detect a cadence from date intervals:
   - monthly, quarterly, or yearly
4. Score confidence using:
   - cadence fit ratio
   - observation coverage (count/span)
   - amount consistency (MAD/median)
   - soft signal boosts/penalties from categories, comments, and payee keywords
5. Classify each candidate as:
   - recurring (subscription-like)
   - recurring_bill (bill/payment-like)
6. Estimate monthly/yearly cost from cadence and median amount.
7. Apply filters (minimum confidence/count/charge, stale/inactive rules, include_bills).

If a whole payee group fails detection, the detector attempts an amount-cluster
fallback so a merchant with multiple plans/prices can still produce a valid
recurring candidate.

Returned items include confidence, cadence, cost estimates, accounts/categories,
and short human-readable reasons to explain why each candidate was surfaced.
"""
import datetime, statistics
from collections import Counter, defaultdict
from decimal import Decimal
from . import utils as butils
from .models import Transaction


class RecurringDetector:
    MIN_CHARGE = Decimal('5.00')
    COMMENT_TAGS = {'sub', 'subscription', 'recurring', 'renewal', 'autopay'}
    RECURRING_CATEGORY_WORDS = {'subscription', 'subscriptions', 'software, games', 'software'}
    BILL_CATEGORY_WORDS = {'loan', 'loans', 'mortgage', 'transfers', 'ignored', 'utilities', 'insurance', 'taxes', 'medical'}
    BILL_PAYEE_WORDS = {'pymt', 'payment', 'loan', 'mortgage', 'cardmember', 'autopay', 'ach', 'taxpymt'}
    RECURRING_PAYEE_WORDS = {'subscription', 'subscrip', 'premium', 'plus', 'membership', 'member', 'dues', 'stream'}
    AGGREGATOR_TOKENS = {'google', 'apple', 'amazon', 'paypal', 'sq', 'amz'}
    CADENCE_RANGES = {'monthly':(24,40), 'quarterly':(75,110), 'yearly':(330,400)}
    STALE_DAYS_BY_CADENCE = {'monthly':62, 'quarterly':150, 'yearly':548}
    MAX_INACTIVE_DAYS_BY_CADENCE = {'monthly':365}

    @classmethod
    def detect(cls, user, lookback_days=913, min_count=3, min_confidence=45, include_bills=False, include_inactive=False):
        """Detect likely recurring payments directly from transactions without profile tables."""
        mindate = datetime.date.today() - datetime.timedelta(days=lookback_days)
        trxs = Transaction.objects.filter(user=user, amount__lt=0, date__gte=mindate)
        trxs = trxs.select_related('account', 'category').order_by('date', 'id')
        # Group transactions by payee key
        grouped = defaultdict(list)
        for trx in trxs:
            key = butils.scrub_payee(trx.payee)
            if len(key) < 3: continue
            grouped[key].append(trx)
        print('-----------')
        for key, rows in grouped.items():
            print(f'{rows[0].payee}  ->  {key}')
        # Detect recurring patterns within each group and assign confidence scores
        items = []
        for key, rows in grouped.items():
            if len(rows) < 2:
                continue
            candidates = []
            detected = cls.detect_group(key, rows)
            if detected:
                candidates.append(detected)
            else:
                for subgroup in cls.split_rows_by_amount(rows):
                    item = cls.detect_group(key, subgroup)
                    if item:
                        item['key'] = f"{item['key']}|{item['median_amount']}"
                        item['reasons'] = item['reasons'] + ['Amount-cluster fallback']
                        candidates.append(item)
            for item in candidates:
                required_count = min_count if item['cadence'] == 'monthly' else 2
                if item['count'] < required_count:
                    continue
                if Decimal(item['median_amount']) < cls.MIN_CHARGE:
                    continue
                max_days = cls.MAX_INACTIVE_DAYS_BY_CADENCE.get(item['cadence'])
                if max_days and item['days_since_last'] > max_days:
                    continue
                if item['is_stale'] and not include_inactive:
                    continue
                if not include_bills and item['kind'] != 'recurring':
                    continue
                if item['confidence'] >= min_confidence:
                    items.append(item)
        # Sort by confidence, cost, count
        items = sorted(items, key=lambda item: (item['confidence'], item['yearly_cost'], item['count']), reverse=True)
        monthly_total = sum([item['monthly_cost'] for item in items])
        yearly_total = sum([item['yearly_cost'] for item in items])
        return {
            'items': items,
            'count': len(items),
            'monthly_total': round(Decimal(monthly_total), 2),
            'yearly_total': round(Decimal(yearly_total), 2),
        }

    @classmethod
    def detect_group(cls, key, rows):
        """ Compute cadence, confidence and cost estimates for one recurring payee group. """
        rows = sorted(rows, key=lambda trx: trx.date)
        span_days = (rows[-1].date - rows[0].date).days
        if span_days < 70:
            return None
        intervals = cls.intervals(rows)
        if len(intervals) == 0:
            return None
        cadence, cadence_ratio = cls.detect_cadence(intervals)
        if cadence_ratio < 0.40:
            return None
        amounts = [abs(Decimal(trx.amount)) for trx in rows]
        median_amount = Decimal(str(statistics.median([float(amount) for amount in amounts])))
        variability = cls.amount_variability(amounts, median_amount)
        occurrence_score = min(20.0, (len(rows) / 18.0) * 10 + (span_days / 365.0) * 10)
        cadence_score = min(45.0, cadence_ratio * 45.0)
        amount_score = max(0.0, 20.0 * (1 - min(variability, 0.9) / 0.9))
        signal_score, reasons = cls.signal_adjustments(rows, key)
        if cadence == 'yearly' and len(rows) <= 3:
            signal_score += 6
            reasons.append('Sparse yearly cadence boost')
        kind, kind_score = cls.classify_kind(rows, key, median_amount, cadence)
        confidence = max(0, min(100, round(cadence_score + occurrence_score + amount_score + signal_score)))
        monthly_cost, yearly_cost = cls.estimate_cost(cadence, median_amount, intervals)
        display_name = cls.display_name(rows)
        accounts = sorted({trx.account.name for trx in rows})
        categories = sorted({trx.category.name for trx in rows if trx.category})
        reasons = [f'{cadence.capitalize()} interval match {(cadence_ratio * 100):.0f}%'] + reasons
        days_since_last = (datetime.date.today() - rows[-1].date).days
        stale_days = cls.STALE_DAYS_BY_CADENCE.get(cadence, 548)
        return {
            'key': key,
            'display_name': display_name,
            'confidence': confidence,
            'kind': kind,
            'kind_score': kind_score,
            'cadence': cadence,
            'count': len(rows),
            'first_date': rows[0].date,
            'last_date': rows[-1].date,
            'days_since_last': days_since_last,
            'is_stale': days_since_last > stale_days,
            'median_amount': round(median_amount, 2),
            'monthly_cost': round(monthly_cost, 2),
            'yearly_cost': round(yearly_cost, 2),
            'amount_variability': round(variability, 3),
            'accounts': accounts,
            'category_names': categories,
            'reasons': reasons[:4],
        }

    @classmethod
    def intervals(cls, rows):
        """Return list of day intervals between adjacent dates."""
        values = []
        for i in range(1, len(rows)):
            delta = (rows[i].date - rows[i - 1].date).days
            if delta > 0:
                values.append(delta)
        return values

    @classmethod
    def detect_cadence(cls, intervals):
        """Pick the cadence with best interval fit ratio."""
        scores = {}
        for cadence, (mindays, maxdays) in cls.CADENCE_RANGES.items():
            matches = [d for d in intervals if d >= mindays and d <= maxdays]
            scores[cadence] = len(matches) / max(len(intervals), 1)
        cadence = max(scores.keys(), key=lambda item: scores[item])
        return cadence, scores[cadence]

    @classmethod
    def amount_variability(cls, amounts, median_amount):
        """Robust variability using MAD / median for amount drift tolerance."""
        if median_amount <= 0:
            return 1.0
        deviations = [abs(float(amount - median_amount)) for amount in amounts]
        mad = statistics.median(deviations) if deviations else 0
        return float(mad / float(median_amount))

    @classmethod
    def signal_adjustments(cls, rows, key):
        """Return score adjustments and human-readable reasons from soft signals."""
        score = 0.0
        reasons = []
        categories = {trx.category.name.lower() for trx in rows if trx.category and trx.category.name}
        comments = ' '.join([(trx.comment or '').lower() for trx in rows])
        if any([word in categories for word in cls.RECURRING_CATEGORY_WORDS]):
            score += 10
            reasons.append('Recurring category boost')
        if any([word in comments for word in cls.COMMENT_TAGS]):
            score += 8
            reasons.append('Comment tag boost')
        if any([word in categories for word in cls.BILL_CATEGORY_WORDS]):
            score -= 16
            reasons.append('Bill-like category penalty')
        key_tokens = set(key.split())
        if len(key_tokens & cls.BILL_PAYEE_WORDS) > 0:
            score -= 12
            reasons.append('Bill/payment keyword penalty')
        return score, reasons

    @classmethod
    def classify_kind(cls, rows, key, median_amount, cadence):
        """Classify recurring groups as recurring-like or recurring bill-like."""
        score = 0
        categories = {trx.category.name.lower() for trx in rows if trx.category and trx.category.name}
        comments = ' '.join([(trx.comment or '').lower() for trx in rows])
        key_tokens = set(key.split())
        non_aggregator_tokens = [token for token in key_tokens if token not in cls.AGGREGATOR_TOKENS]
        if any([word in categories for word in cls.RECURRING_CATEGORY_WORDS]):
            score += 2
        if any([word in comments for word in cls.COMMENT_TAGS]):
            score += 1
        if len([word for word in cls.RECURRING_PAYEE_WORDS if word in key]) > 0:
            score += 1
        if cadence in {'monthly', 'yearly'}:
            score += 1
        if median_amount <= 80:
            score += 1
        if len(non_aggregator_tokens) >= 1:
            score += 1
        if cadence == 'yearly' and len(rows) <= 3 and len(non_aggregator_tokens) >= 1:
            score += 1
        if any([word in categories for word in cls.BILL_CATEGORY_WORDS]):
            score -= 2
        if len(key_tokens & cls.BILL_PAYEE_WORDS) > 0:
            score -= 1
        if median_amount >= 150 and score <= 0:
            score -= 1
        kind = 'recurring' if score >= 3 else 'recurring_bill'
        return kind, score

    @classmethod
    def display_name(cls, rows):
        """Use the most common original payee as the display label."""
        counter = Counter([' '.join((trx.payee or '').split()) for trx in rows if trx.payee])
        if len(counter) == 0:
            return rows[-1].payee if rows[-1].payee else 'Unknown Payee'
        return counter.most_common(1)[0][0]

    @classmethod
    def estimate_cost(cls, cadence, median_amount, intervals):
        """Convert detected cadence and amount into monthly/yearly estimates."""
        if cadence == 'monthly':
            monthly = median_amount
            yearly = median_amount * Decimal(12)
            return monthly, yearly
        if cadence == 'yearly':
            monthly = median_amount / Decimal(12)
            yearly = median_amount
            return monthly, yearly
        if cadence == 'quarterly':
            monthly = median_amount / Decimal(3)
            yearly = median_amount * Decimal(4)
            return monthly, yearly
        avg_interval = statistics.mean(intervals) if len(intervals) else 30
        monthly = median_amount * Decimal(30.4375 / max(avg_interval, 1))
        yearly = monthly * Decimal(12)
        return monthly, yearly

    @classmethod
    def split_rows_by_amount(cls, rows):
        """Split a merchant group by amount bands to handle multi-plan merchants."""
        clusters = []
        for trx in sorted(rows, key=lambda item: abs(Decimal(item.amount))):
            amount = abs(Decimal(trx.amount))
            placed = False
            for cluster in clusters:
                center = cluster['center']
                tolerance = max(Decimal('1.50'), center * Decimal('0.18'))
                if abs(amount - center) <= tolerance:
                    cluster['rows'].append(trx)
                    values = [abs(Decimal(item.amount)) for item in cluster['rows']]
                    cluster['center'] = Decimal(str(statistics.mean([float(v) for v in values])))
                    placed = True
                    break
            if not placed:
                clusters.append({'center': amount, 'rows': [trx]})
        return [cluster['rows'] for cluster in clusters if len(cluster['rows']) >= 2]

    @classmethod
    def is_stale(cls, item):
        """True when the recurring series is too old to surface in recurring view."""
        last_date = item.get('last_date')
        if not last_date:
            return True
        cadence = item.get('cadence')
        stale_days = cls.STALE_DAYS_BY_CADENCE.get(cadence, 548)
        days_since_last = (datetime.date.today() - last_date).days
        return days_since_last > stale_days
