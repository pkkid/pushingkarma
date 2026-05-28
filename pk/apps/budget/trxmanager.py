# encoding: utf-8
# https://github.com/csingley/ofxtools
# https://ofxtools.readthedocs.io/en/latest/
import csv, datetime, fnmatch, re, logging
from collections import defaultdict
from django.conf import settings
from decimal import Decimal
from hashlib import md5
from io import StringIO
from ofxtools.Parser import OFXTree
from pk.utils.utils import rget
from .models import Account, Transaction
from .utils import scrub_payee
log = logging.getLogger(__name__)


class TransactionManager:
  
    def __init__(self, user, safe=False, save=False):
        self.user = user        # User transactions belong to
        self.safe = safe        # unique trxs based on date, payee and amount
        self.save = save        # Save db changes
    
    def import_file(self, filename, filehandle):
        """ Main entrypoint for importing transactions. """
        for account in Account.objects.filter(user=self.user):
            rules = account.rules or {}
            pattern = rules.get('file_pattern')
            if pattern and fnmatch.fnmatch(filename, pattern):
                log.info(f'Importing transactions for {self.user.email} {account.name}')
                ext = filename.split('.')[-1].lower()
                account, trxs = getattr(self, f'_read_{ext}')(account, rules, filehandle)
                for trx in trxs:
                    trx.user = self.user
                    trx.account_id = account.id
                    trx.original_date = trx.date
                    trx.original_payee = trx.payee
                    trx.original_amount = trx.amount
                self.categorize_transactions(self.user, account, trxs)
                if self.save is True:
                    account.save()
                    trxs = self._bulk_create(account, trxs)
                return self._summarize(filename, account, trxs)
        raise Exception(f'No matching account for {filename}')

    def _read_csv(self, account, rules, filehandle):
        """ Returns an updated account and list of transactions from the csv file. """
        transactions = []
        rows = list(csv.DictReader(StringIO(filehandle.read().decode())))
        dateformat = rget(account, 'rules.date_format')
        for row in self.sort(rows, rules):
            date = self.clean_date(rget(row, rget(rules, 'columns.date')), dateformat)
            payee = self.clean_payee(rget(row, rget(rules, 'columns.payee'))) or ''
            amount = self.clean_amount(rget(row, rget(rules, 'columns.amount')))
            amount = -amount if rules.get('inverse_amounts') is True else amount
            balance = self.clean_amount(rget(row, rget(rules, 'columns.balance')))
            trxid = rget(row, rget(rules, 'columns.trxid')) or \
                md5(f'{date}{payee}{amount}{balance}'.encode()).hexdigest()
            transactions.append(Transaction(trxid=trxid, date=date, payee=payee, amount=amount))
        account.balance = balance
        account.balance_updated = date
        return account, transactions

    def _read_qfx(self, account, rules, filehandle):
        """ Returns an updated account and list of transactions from the qfx file. """
        transactions = []
        parser = OFXTree()
        parser.parse(filehandle)
        ofx = parser.convert()
        rows = list(rget(ofx, rget(rules, 'transactions')))
        dateformat = rget(account, 'rules.date_format')
        for row in self.sort(rows, rules):
            date = self.clean_date(rget(row, rget(rules, 'columns.date')), dateformat)
            payee = self.clean_payee(rget(row, rget(rules, 'columns.payee'))) or ''
            amount = self.clean_amount(rget(row, rget(rules, 'columns.amount')))
            amount = -amount if rules.get('inverse_amounts') is True else amount
            trxid = rget(row, rget(rules, 'columns.trxid')) or \
                md5(f'{date}{payee}{amount}'.encode()).hexdigest()
            transactions.append(Transaction(trxid=trxid, date=date, payee=payee, amount=amount))
        account.balance = rget(ofx, rget(rules, 'balance'))
        account.balance_updated = date
        return account, transactions
    
    def _bulk_create(self, account, trxs):
        """ Bulk create transactions in the database. Made a custom function
            here so we can properly track the newly created items.
        """
        newtrxs = []
        unique_fields = ['date', 'payee', 'amount'] if self.safe else ['trxid']
        existing = set(Transaction.objects.filter(user=self.user, account=account).values_list(*unique_fields))
        for trx in trxs:
            key = tuple(getattr(trx, field) for field in unique_fields)
            if key not in existing: newtrxs.append(trx)
        Transaction.objects.bulk_create(newtrxs, unique_fields=unique_fields)
        return newtrxs

    def _summarize(self, filename, account, trxs):
        """ Summarize the transactions created. """
        metrics = dict(
            filename = filename,
            created = len(trxs),
            categorized = len([trx for trx in trxs if trx.category_id]),
            mindate = min([trx.date for trx in trxs]) if len(trxs) else None,
            maxdate = max([trx.date for trx in trxs]) if len(trxs) else None,
            safe = self.safe,
            account = dict(url=account.url, name=account.name),
        )
        log.info(f'Imported {metrics["created"]} transactions to account {account.name} for {self.user.email}')
        return metrics
    
    @classmethod
    def sort(cls, rows, rules):
        """ Returns the rows in sorted order. """
        if len(rows) < 2: return rows
        dateformat = rget(rules, 'date_format')
        first_date = cls.clean_date(rget(rows[0], rget(rules, 'columns.date')), dateformat)
        last_date = cls.clean_date(rget(rows[-1], rget(rules, 'columns.date')), dateformat)
        return reversed(rows) if first_date > last_date else rows

    @classmethod
    def categorize_transactions(cls, user, account, trxs, daysback=730, skip_categorized=True, source_trxs=None):
        """ Categorize transactions from payee history and return updated items. """
        updated = []
        history = cls.category_history(user, account, daysback=daysback, source_trxs=source_trxs)
        for trx in trxs:
            if skip_categorized and trx.category_id: continue
            newcategoryid = cls.match_category(trx, history, daysback=daysback)
            if newcategoryid and newcategoryid != trx.category_id:
                trx.category_id = newcategoryid
                updated.append(trx)
        return updated
    
    @classmethod
    def category_history(cls, user, account, daysback=730, source_trxs=None):
        """ Returns categorized transaction history used for matching. """
        history = []
        if source_trxs is None:
            mindate = datetime.date.today() - datetime.timedelta(days=daysback)
            source_trxs = Transaction.objects.filter(user=user, account=account, category__isnull=False, date__gte=mindate)
        for trx in source_trxs:
            payee = trx['payee'] if isinstance(trx, dict) else trx.payee
            categoryid = trx['category_id'] if isinstance(trx, dict) else trx.category_id
            amount = trx['amount'] if isinstance(trx, dict) else trx.amount
            date = trx['date'] if isinstance(trx, dict) else trx.date
            if not categoryid:
                continue
            if cls.has_stopword(payee):
                continue
            scrubbed = scrub_payee(payee)
            tokens = scrubbed.split()
            if len(scrubbed) < 3 or len(tokens) == 0:
                continue
            history.append(dict(scrubbed=scrubbed, tokens=tokens, category_id=categoryid,
                date=date, sign=cls.amount_sign(amount)))
        return history

    @classmethod
    def match_category(cls, trx, history, daysback=730):
        """ Return the highest confidence category id for the transaction. """
        if cls.has_stopword(trx.payee):
            return None
        scrubbed = scrub_payee(trx.payee)
        tokens = scrubbed.split()
        if len(scrubbed) < 3 or len(tokens) == 0:
            return None
        scores = defaultdict(float)
        target_sign = cls.amount_sign(trx.amount)
        for item in history:
            if target_sign != 0 and item['sign'] != 0 and item['sign'] != target_sign:
                continue
            score = cls.match_score(scrubbed, tokens, item, daysback)
            if score > 0: scores[item['category_id']] += score  # Additive scoring for multiple signals
        if len(scores) == 0: return None  # No signals for this transaction
        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        top_categoryid, top_score = ranked[0]
        second_score = ranked[1][1] if len(ranked) > 1 else 0
        if top_score < 5: return None  # Not a strong enough signal
        if second_score and top_score < second_score * 1.35: return None  # Not better than the next best signal
        if second_score and top_score - second_score < 1.5: return None  # Not strong margin over the next best signal
        return top_categoryid

    @classmethod
    def match_score(cls, scrubbed, tokens, item, daysback=730):
        """ Return match score between a transaction and a history item. """
        # Only use the first two words for keyword matching signals.
        # Trailing tokens are often noisy (location/help/reference fragments).
        left_tokens = tokens[:2]
        right_tokens = item['tokens'][:2]
        shared = set(left_tokens) & set(right_tokens)
        if len(shared) == 0: return 0  # No shared tokens means no match
        common_prefix = 0
        for i in range(min(len(left_tokens), len(right_tokens))):
            if left_tokens[i] != right_tokens[i]: break
            common_prefix += 1
        score = 0
        # 10: Exact match on scrubbed payee is a very strong signal
        # 4+: Common prefix is a strong signal
        # 3:  Matching first token is a strong signal
        # 1+: Each shared token is a signal
        if scrubbed == item['scrubbed']: score += 10  
        if common_prefix > 0: score += 4 + ((common_prefix - 1) * 2)  
        if left_tokens[0] == right_tokens[0]: score += 3  
        score += sum([1 / (i + 1) for i, token in enumerate(left_tokens) if token in shared])  
        return score * cls.recency_weight(item['date'], daysback)

    @classmethod
    def recency_weight(cls, date, daysback=730):
        """ Return recency multiplier for historical categorization signal. """
        daysold = max((datetime.date.today() - date).days, 0)
        return max(0.35, 1 - ((daysold / max(daysback, 1)) * 0.65))

    @classmethod
    def amount_sign(cls, amount):
        """ Return -1 for debit, 1 for credit and 0 for zero amount. """
        if amount < 0: return -1
        if amount > 0: return 1
        return 0

    @classmethod
    def has_stopword(cls, payee):
        """ True if payee includes a configured categorization stopword. """
        stopwords = settings.BUDGET_CATEGORY_STOPWORDS
        if len(stopwords) == 0: return False
        normalized = ' '.join(re.sub(r'[^a-z0-9 ]', ' ', (payee or '').lower()).split())
        if len(normalized) == 0: return False
        tokens = set(normalized.split())
        for stopword in stopwords:
            if ' ' in stopword:
                if stopword in normalized: return True
                continue
            if stopword in tokens: return True
        return False
    
    @classmethod
    def clean_date(cls, date, dateformat=None):
        """ Clean the date value. """
        if isinstance(date, str):
            return datetime.datetime.strptime(date, dateformat).date()
        if isinstance(date, datetime.datetime):
            return date.date()
        return date
    
    @classmethod
    def clean_amount(cls, amount):
        """ Clean amount value and return a decimal. """
        if isinstance(amount, Decimal):
            return amount
        if isinstance(amount, str):
            amount = Decimal(re.sub(r'[^\-*\d.]', '', amount))
        return amount
    
    @classmethod
    def clean_payee(cls, payee):
        """ Clean payee string when saving new trxs to the db. """
        payee = payee.replace('ELECTRONIC WITHDRAWAL', '')
        payee = payee.replace('ELECTRONIC DEPOSIT', '')
        payee = ' '.join([word for word in payee.split()])
        payee = payee.strip(' -')
        return payee
