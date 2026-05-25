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
5. Merge amount-split groups with the same name when their date ranges do not
    overlap (e.g., old price vs new price periods).
6. Filter out inactive items unless include_inactive is set.
7. Return items sorted by cadence and name, with total monthly/yearly cost.
"""
import datetime, logging, statistics
from decimal import Decimal
from django.conf import settings
from django_searchquery.search import Search
from pk.utils.utils import Bunch
from . import utils as butils
from .models import Transaction
log = logging.getLogger(__name__)


class RecurringManager:
    """ Manager class for recurring payment detection. """
    THRESHOLD_AMOUNT = Decimal('0.6')
    THRESHOLD_DAYS = {'monthly':7, 'yearly':7}
    MIN_ACTIVE_DAYS = {'monthly':62, 'yearly':375}
    MIN_SPAN_DAYS = {'monthly':60, 'yearly':355}
    MIN_TRXS = {'monthly':3, 'yearly':2}
    MIN_CADENCE_RATIO = {'monthly':0.4, 'yearly':0.4}
    MAX_PINPONG_RATIO = {'monthly':0.4, 'yearly':0.4}
    MAX_VARIABILITY = {'monthly':0.6, 'yearly':0.8}
    SKIP_CATEGORIES = getattr(settings, 'BUDGET_RECURRING_SKIP_CATEORIES', {})

    CADENCE_RANGES = {}
    CADENCE_RANGES['monthly'] = (28-THRESHOLD_DAYS['monthly'], 31+THRESHOLD_DAYS['monthly'])
    CADENCE_RANGES['yearly'] = (365-THRESHOLD_DAYS['yearly'], 365+THRESHOLD_DAYS['yearly'])

    def __init__(self, user, search='', searchfields=None):
        self.user = user                        # User transactions belong to
        self.search = (search or '').strip()    # Optional search filter for test/debug scenarios
        self.searchfields = searchfields        # Optional list of fields to apply search filter
        self.items = []                         # List of detected recurring items
        self._find_recurring()                  # Run the detection algorithm

    def _find_recurring(self):
        """ Detect likely recurring payments directly from transactions without profile tables. """
        trxs = Transaction.objects.filter(user=self.user, amount__lt=0)
        if self.search and self.searchfields:
            trxs = Search(self.searchfields).get_queryset(trxs, self.search)
        trxs = trxs.exclude(category__name__in=self.SKIP_CATEGORIES)
        trxs = trxs.select_related('account', 'category').order_by('date', 'id')
        groups = self._group_by_payee_and_amount(trxs)
        log.debug(f'Analyzing {len(groups)} groups from {len(trxs)} trxs for recurring transactions')
        for group in groups:
            if item := self._analyze_group(group):
                self.items.append(item)
        self.items = self._check_merge_items(self.items)
        self.items = sorted(self.items, key=lambda item: (item.cadence, item.name))

    def _group_by_payee_and_amount(self, trxs):
        """ Group transactions by payee and amount. """
        groups = []
        for trx in trxs:
            name = butils.scrub_payee(trx.payee)
            amount = trx.amount
            for group in groups:
                if group.name != name: continue
                threshold = abs(group.average) * self.THRESHOLD_AMOUNT
                if amount-threshold <= group.average <= amount+threshold:
                    values = [Decimal(trx.amount) for trx in group.trxs]
                    group.average = Decimal(str(sum(values) / len(values)))
                    group.trxs.append(trx)
                    break
            else:
                groups.append(Bunch(name=name, trxs=[trx], average=amount))
        # Only keep groups with at least 2 transactions
        return [grp for grp in groups if len(grp.trxs) >= 2]

    def _check_merge_items(self, items):
        """ Merge items with the same name when their date ranges do not overlap. """
        merged = []
        for i in items:
            for m in merged:
                if i.name != m.name or m.cadence != i.cadence:
                    continue
                if i.last_date < m.first_date or i.first_date > m.last_date:
                    m.trxs.extend(i.trxs)
                    m.amounts = [Decimal(trx.amount) for trx in m.trxs]
                    self._collect_metrics(m)
                    break
            else:
                merged.append(i)
        return merged

    def _analyze_group(self, group):
        """ Compute cadence, confidence and cost estimates for one recurring payee group. """
        item = Bunch(name=group.name)
        item.trxs = sorted(group.trxs, key=lambda trx: trx.date)
        item.amounts = [Decimal(trx.amount) for trx in item.trxs]
        item.daysago = (datetime.date.today() - item.trxs[-1].date).days
        item.cadence, item.cadenceratio = self._get_cadence_ratio(item)
        # Peform checks to confirm group meets criteria for recurring payments.
        # If any check fails, return None to reject the group.
        if not self._check_cadence_ratio(item): return None
        if not self._check_span_days(item): return None
        if not self._check_min_trxs(item): return None
        if not self._check_ping_pong(item): return None
        if not self._check_variability(item): return None
        return self._collect_metrics(item)

    def _collect_metrics(self, item):
        """ Update metrics for an item after merging or amount splitting. """
        item.count = len(item.trxs)
        item.first_date = min(trx.date for trx in item.trxs)
        item.last_date = max(trx.date for trx in item.trxs)
        item.first_amount = round(item.amounts[0], 2)
        item.last_amount = round(item.amounts[-1], 2)
        item.max_amount = round(max(item.amounts), 2)
        item.min_amount = round(min(item.amounts), 2)
        item.average = round(sum(item.amounts) / len(item.amounts), 2)
        item.is_active = self.MIN_ACTIVE_DAYS[item.cadence] >= item.daysago
        item.accounts = sorted({trx.account.name for trx in item.trxs})
        item.categories = sorted({trx.category.name for trx in item.trxs if trx.category})
        return item

    def _get_cadence_ratio(self, item):
        """ Pick the cadence with best interval fit ratio. Returns:
            - cadence: 'monthly' or 'yearly'
            - cadence_ratio: Percent intervals that match cadence range
        """
        scores = {}
        intervals = [(item.trxs[i].date - item.trxs[i-1].date).days for i in range(1, len(item.trxs))]
        intervals = list(filter(lambda x: x > 0, intervals))
        for cadence, (mindays, maxdays) in self.CADENCE_RANGES.items():
            matches = [d for d in intervals if d >= mindays and d <= maxdays]
            scores[cadence] = len(matches) / max(len(intervals), 1)
        cadence = max(scores.keys(), key=lambda item: scores[item])
        return cadence, scores[cadence]

    def _check_cadence_ratio(self, item):
        """ Check if the cadence ratio meets the threshold for any cadence. """
        minratio = self.MIN_CADENCE_RATIO[item.cadence]
        if item.cadenceratio < minratio:
            log.debug(f' - Cadence Ratio {item.cadenceratio:.2f} < {minratio:.2f}: {item.name}')
            return False
        return True

    def _check_span_days(self, item):
        """ Check the transaction dates span enough days. """
        minspan = self.MIN_SPAN_DAYS[item.cadence]
        spandays = (item.trxs[-1].date - item.trxs[0].date).days
        if spandays < minspan:
            log.debug(f' - Span Days {spandays} < {minspan}: {item.name}')
            return False
        return True

    def _check_min_trxs(self, item):
        """ Check the minimum number of transactions for the cadence. """
        mintrxs = max(2, self.MIN_TRXS[item.cadence])
        if len(item.trxs) < mintrxs:
            log.debug(f' - Num Transactions {len(item.trxs)} < {mintrxs}: {item.name}')
            return False
        return True

    def _check_ping_pong(self, item):
        """ Check amounts do not ping-pong up/down. """
        diffs = [item.amounts[i] - item.amounts[i-1] for i in range(1, len(item.amounts))]
        hasincrease = any(d > 0 for d in diffs)
        hasdecrease = any(d < 0 for d in diffs)
        ppratio = sum(1 for d in diffs if d != 0) / len(diffs)
        maxratio = self.MAX_PINPONG_RATIO[item.cadence]
        if hasincrease and hasdecrease and ppratio > maxratio:
            log.debug(f' - Amounts PingPong {ppratio:.2f} > {maxratio:.2f}: {item.name}')
            return False
        return True

    def _check_variability(self, item):
        """ Check amount variablity is not too high. """
        # Calculate the variability of amounts relative to median
        median = statistics.median(item.amounts)
        deviations = [abs(amount - median) for amount in item.amounts]
        mad = statistics.median(deviations) if deviations else Decimal('0')
        variability = float(mad / abs(median)) if abs(median) else 0.0
        # Check the variability is within the threshold for the cadence
        maxvariability = self.MAX_VARIABILITY[item.cadence]
        if variability > maxvariability:
            log.debug(f' - Amount Variability {variability:.2f} > {maxvariability:.2f}: {item.name}')
            return False
        return True
