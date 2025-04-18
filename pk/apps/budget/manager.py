# encoding: utf-8
# https://github.com/csingley/ofxtools
# https://ofxtools.readthedocs.io/en/latest/
import csv, datetime, fnmatch, re, logging
from decimal import Decimal
from hashlib import md5
from io import StringIO
from ofxtools.Parser import OFXTree
from pk.utils.utils import rget
from .models import Account, Transaction
log = logging.getLogger(__name__)


class TransactionManager:
  
    def __init__(self, request, safeimport=False, test=False):
        self.request = request          # Request object for reverse url
        self.user = request.user        # User transactions belong to
        self.safeimport = safeimport    # unique trxs based on date, payee and amount
        self.test = test                # Test mode, no db changes
    
    def import_file(self, filename, filehandle):
        """ Main entrypoint for importing transactions. """
        for account in Account.objects.filter(user=self.user):
            rules = account.import_rules or {}
            pattern = rules.get('file_pattern')
            if pattern and fnmatch.fnmatch(filename, pattern):
                log.info(f'Importing transactions for {self.user.email} {account.name}')
                ext = filename.split('.')[-1].lower()
                account, trxs = getattr(self, f'_read_{ext}')(account, rules, filehandle)
                categories = self._categories(account)
                for trx in trxs:
                    trx.user = self.user
                    trx.account_id = account.id
                    trx.original_date = trx.date
                    trx.original_payee = trx.payee
                    trx.original_amount = trx.amount
                    trx.category_id = categories.get(trx.payee.lower())
                if not self.test:
                    account.save()
                    unique_fields = ['date','payee','amount'] if self.safeimport else ['trxid']
                    trxs = Transaction.objects.bulk_create(trxs, unique_fields=unique_fields)
                return self._summarize(filename, account, trxs)
        raise Exception(f'No matching account for {filename}')

    def _read_csv(self, account, rules, filehandle):
        """ Returns an updated account and list of transactions from the csv file. """
        transactions = []
        rows = list(csv.DictReader(StringIO(filehandle.read().decode())))
        dateformat = rget(account, 'import_rules.date_format')
        for row in self._sorted(rows, rules):
            date = self._clean_date(rget(row, rget(rules, 'columns.date')), dateformat)
            payee = self._clean_payee(rget(row, rget(rules, 'columns.payee'))) or ''
            amount = self._clean_amount(rget(row, rget(rules, 'columns.amount')))
            balance = self._clean_amount(rget(row, rget(rules, 'columns.balance')))
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
        dateformat = rget(account, 'import_rules.date_format')
        for row in self._sorted(rows, rules):
            date = self._clean_date(rget(row, rget(rules, 'columns.date')), dateformat)
            payee = self._clean_payee(rget(row, rget(rules, 'columns.payee'))) or ''
            amount = self._clean_amount(rget(row, rget(rules, 'columns.amount')))
            trxid = rget(row, rget(rules, 'columns.trxid')) or \
                md5(f'{date}{payee}{amount}'.encode()).hexdigest()
            transactions.append(Transaction(trxid=trxid, date=date, payee=payee, amount=amount))
        account.balance = rget(ofx, rget(rules, 'balance'))
        account.balance_updated = rget(ofx, rget(rules, 'balance_date'))
        return account, transactions
    
    def _sorted(self, rows, rules):
        """ Returns the rows in sorted order. """
        if len(rows) < 2: return rows
        dateformat = rget(rules, 'date_format')
        first_date = self._clean_date(rget(rows[0], rget(rules, 'columns.date')), dateformat)
        last_date = self._clean_date(rget(rows[-1], rget(rules, 'columns.date')), dateformat)
        return reversed(rows) if first_date > last_date else rows

    def _summarize(self, filename, account, trxs):
        """ Summarize the transactions created. """
        metrics = dict(
            filename = filename,
            created = len(trxs),
            categorized = len([trx for trx in trxs if trx.category_id]),
            mindate = min([trx.date for trx in trxs]) if len(trxs) else None,
            maxdate = max([trx.date for trx in trxs]) if len(trxs) else None,
            account = dict(url=account.url(self.request), name=account.name),
        )
        log.info(f'Imported {metrics["created"]} transactions to account {account.name}')
        return metrics
    
    def _categories(self, account):
        """ Returns a dict of existing payee -> category """
        mindate = datetime.datetime.now() - datetime.timedelta(days=730)
        trxs = Transaction.objects.filter(user=self.user, account=account, category__isnull=False, date__gte=mindate)
        trxs = trxs.values('payee', 'category_id')
        categories = {self._scrub_payee(trx['payee']):trx['category_id'] for trx in trxs}
        return {payee:catid for payee,catid in categories.items() if len(payee) > 2}
    
    def _clean_date(self, date, dateformat=None):
        """ Clean the date value. """
        if isinstance(date, str):
            return datetime.datetime.strptime(date, dateformat).date()
        if isinstance(date, datetime.datetime):
            return date.date()
        return date
    
    def _clean_amount(self, amount):
        """ Clean amount value and return a decimal. """
        if isinstance(amount, Decimal):
            return amount
        if isinstance(amount, str):
            amount = Decimal(re.sub(r'[^\-*\d.]', '', amount))
        return amount
    
    def _clean_payee(self, payee):
        """ Clean payee string. """
        payee = payee.replace('ELECTRONIC WITHDRAWAL', '')
        payee = payee.replace('ELECTRONIC DEPOSIT', '')
        payee = payee.strip(' -')
        payee = ' '.join([word for word in payee.split()])
        return payee
    
    def _scrub_payee(self, payee):
        """ Scrub unique details from payee when trying to match categories. """
        payee = re.sub(r'[^a-z\. ]', '', payee.lower())             # Remove specical chars
        payee = ' '.join([w for w in payee.split() if len(w) > 1])  # Remove multi-spaces and 1 char words
        return payee.strip()
