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
  
    def __init__(self, user, safe=False, save=False):
        self.user = user        # User transactions belong to
        self.safe = safe        # unique trxs based on date, payee and amount
        self.save = save        # Save db changes
    
    def import_file(self, filename, filehandle):
        """ Main entrypoint for importing transactions. """
        for account in Account.objects.filter(user=self.user):
            rules = account.import_rules or {}
            pattern = rules.get('file_pattern')
            if pattern and fnmatch.fnmatch(filename, pattern):
                log.info(f'Importing transactions for {self.user.email} {account.name}')
                ext = filename.split('.')[-1].lower()
                account, trxs = getattr(self, f'_read_{ext}')(account, rules, filehandle)
                payee_categoryids = self.payee_categoryids(self.user, account)
                for trx in trxs:
                    trx.user = self.user
                    trx.account_id = account.id
                    trx.original_date = trx.date
                    trx.original_payee = trx.payee
                    trx.original_amount = trx.amount
                    trx.category_id = payee_categoryids.get(trx.payee.lower())
                if self.save is True:
                    account.save()
                    trxs = self._bulk_create(account, trxs)
                return self._summarize(filename, account, trxs)
        raise Exception(f'No matching account for {filename}')

    def _read_csv(self, account, rules, filehandle):
        """ Returns an updated account and list of transactions from the csv file. """
        transactions = []
        rows = list(csv.DictReader(StringIO(filehandle.read().decode())))
        dateformat = rget(account, 'import_rules.date_format')
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
        dateformat = rget(account, 'import_rules.date_format')
        for row in self.sort(rows, rules):
            date = self.clean_date(rget(row, rget(rules, 'columns.date')), dateformat)
            payee = self.clean_payee(rget(row, rget(rules, 'columns.payee'))) or ''
            amount = self.clean_amount(rget(row, rget(rules, 'columns.amount')))
            amount = -amount if rules.get('inverse_amounts') is True else amount
            trxid = rget(row, rget(rules, 'columns.trxid')) or \
                md5(f'{date}{payee}{amount}'.encode()).hexdigest()
            transactions.append(Transaction(trxid=trxid, date=date, payee=payee, amount=amount))
        account.balance = rget(ofx, rget(rules, 'balance'))
        account.balance_updated = rget(ofx, rget(rules, 'balance_date'))
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
    def payee_categoryids(cls, user, account, daysback=730):
        """ Returns a dict of existing payee -> category """
        mindate = datetime.datetime.now() - datetime.timedelta(days=daysback)
        trxs = Transaction.objects.filter(user=user, account=account, category__isnull=False, date__gte=mindate)
        trxs = trxs.values('payee', 'category_id')
        categories = {cls.scrub_payee(trx['payee']):trx['category_id'] for trx in trxs}
        return {payee:catid for payee,catid in categories.items() if len(payee) > 2}
    
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
        """ Clean payee string. """
        payee = payee.replace('ELECTRONIC WITHDRAWAL', '')
        payee = payee.replace('ELECTRONIC DEPOSIT', '')
        payee = ' '.join([word for word in payee.split()])
        payee = payee.strip(' -')
        return payee
    
    @classmethod
    def scrub_payee(cls, payee):
        """ Scrub unique details from payee when trying to match categories. """
        payee = re.sub(r'[^a-z\. ]', '', payee.lower())             # Remove specical chars
        payee = ' '.join([w for w in payee.split() if len(w) > 1])  # Remove multi-spaces and 1 char words
        return payee.strip()
