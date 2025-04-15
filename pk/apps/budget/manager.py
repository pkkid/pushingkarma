# encoding: utf-8
# https://github.com/csingley/ofxtools
# https://ofxtools.readthedocs.io/en/latest/
import csv, datetime, fnmatch, re, logging
from .models import Account
from base64 import b64encode
from decimal import Decimal
from hashlib import md5
from io import StringIO
from ofxtools.Parser import OFXTree
from pk.utils.utils import rget
log = logging.getLogger(__name__)

REMOVE = "'"
KEEP = ' ./'
CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
NUMS = '0123456789'


class TransactionManager:
  
    def __init__(self, user):
        self.user = user        # User transactions belong to
        self.status = {}        # Status msg per file
    
    def import_file(self, filename, filehandle):
        """ Main entrypoint for importing transactions. """
        for account in Account.objects.filter(user=self.user):
            rules = account.import_rules or {}
            pattern = rules.get('file_pattern')
            if pattern and fnmatch.fnmatch(filename, pattern):
                log.info(f'Importing transactions for {self.user.email} {account.name}')
                ext = filename.split('.')[-1].lower()
                data = getattr(self, f'_read_{ext}', None)(rules, filehandle)
                import pprint; pprint.pprint(data)
                return None
        raise Exception(f'No matching account for {filename}')

    def _read_csv(self, rules, filehandle):
        """ Returns list of dicts for all transactions in the file. """
        response = {'balance':None, 'balance_updated':None, 'transactions':[]}
        dateformat = rget(rules, 'date_format')
        rows = csv.DictReader(StringIO(filehandle.read().decode()))
        rows = sorted(rows, key=lambda x: self._clean_date(x[rget(rules, 'columns.date')], dateformat))
        for row in rows:
            date = self._clean_date(rget(row, rget(rules, 'columns.date')), dateformat)
            payee = self._clean_payee(rget(row, rget(rules, 'columns.payee')))
            amount = self._clean_amount(rget(row, rget(rules, 'columns.amount')))
            balance = self._clean_amount(rget(row, rget(rules, 'columns.balance')))
            trxid = rget(row, rget(rules, 'columns.trxid')) or \
                md5(f'{date}{payee}{amount}{balance}'.encode()).hexdigest()
            response['transactions'].append({'date':date, 'payee':payee, 'amount':amount, 'trxid':trxid})
            response['balance'] = balance
            response['balance_updated'] = date
        return response

    def _read_qfx(self, rules, filehandle):
        """ Returns list of dicts for all transactions in the file. """
        response = {'balance':None, 'balance_updated':None, 'transactions':[]}
        parser = OFXTree()
        parser.parse(filehandle)
        ofx = parser.convert()
        dateformat = rget(rules, 'date_format')
        for row in rget(ofx, rget(rules, 'transactions')):
            date = self._clean_date(rget(row, rget(rules, 'columns.date')), dateformat)
            payee = self._clean_payee(rget(row, rget(rules, 'columns.payee')))
            amount = self._clean_amount(rget(row, rget(rules, 'columns.amount')))
            trxid = rget(row, rget(rules, 'columns.trxid')) or \
                md5(f'{date}{payee}{amount}'.encode()).hexdigest()
            response['transactions'].append({'date':date, 'payee':payee, 'amount':amount, 'trxid':trxid})
        response['balance'] = self._clean_amount(rget(ofx, rget(rules, 'balance')))
        response['balance_updated'] = self._clean_date(rget(ofx, rget(rules, 'balance_updated')))
        return response
    
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


# ------------------------------
# class TransactionManager:

#     def __init__(self):
#         self.status = []            # status msg per file
#         self.account = None         # account for this qfx file
#         self.categorized = 0        # num transactions categorized
#         self.errors = 0             # num errors encoundered
#         self.files = 0              # num files imported
#         self.labeled = 0            # num transactions labeled
#         self.transactions = 0       # num transactions imported

#     def get_status(self):
#         return {
#             'account': self.account.name,
#             'categorized': self.categorized,
#             'filename': self.filename,
#             'files': self.files,
#             'labeled': self.labeled,
#             'transactions': self.transactions,
#         }

#     @cached_property
#     def _accounts_by_fid(self):
#         return {a.fid:a for a in Account.objects.all()}

#     @cached_property
#     def _accounts_by_name(self):
#         return {a.name:a for a in Account.objects.all()}

#     @cached_property
#     def _existing(self):
#         existing = Transaction.objects.order_by('-date')
#         return existing.values('account__fid','trxid','payee','category__name','amount')

#     @cached_property
#     def _existing_ids(self):
#         return set((trx['account__fid'], trx['trxid']) for trx in self._existing)

#     @cached_property
#     def _existing_categories(self):
#         return {trx['payee'].lower().rstrip('0123456789 '):trx['category__name']
#             for trx in self._existing if trx['payee'] and trx['category__name']}

#     def _transaction_exists(self, trx, addit=False):
#         result = (int(trx['accountfid']), trx['trxid']) in self._existing_ids
#         if result is False and addit is True:
#             self._lazy__existing_ids.add((int(trx['accountfid']), trx['trxid']))
#         return result

#     def import_csv(self, user, filename, handle):
#         """ Import transactions from a csv file. """
#         try:
#             self.files += 1
#             self.filename = filename
#             transactions = []
#             log.info('Importing transactions csv file: %s' % filename)
#             # WARNING: This is auto-choosing the bank account from a generic filename. This
#             # is because DCU stopped allowing us to download qfx files which contain the
#             # bank FID information inside. I am hoping this is temporary.
#             if filename.startswith('Free Checking Transactions') and filename.endswith('.csv'): name = 'DCU'
#             else: raise Exception('Unknown CSV filename.')
#             self.account = self._accounts_by_name[name]
#             # Update transactions
#             csvdata = handle.read().decode()
#             csvdata = csv.DictReader(StringIO(csvdata))
#             balance = None
#             balancedt = None
#             for trx in csvdata:
#                 hashstr = f'{trx["DATE"]}{trx["DESCRIPTION"]}{trx["AMOUNT"]}{trx["CURRENT BALANCE"]}'
#                 trx['trxid'] = base64.b64encode(hashlib.md5(hashstr.encode()).digest()).decode()
#                 trx['accountfid'] = self.account.fid
#                 if not self._transaction_exists(trx, addit=True):
#                     date = datetime.datetime.strptime(trx['DATE'], '%m/%d/%Y')
#                     amount = Decimal(re.sub(r'[^\-*\d.]', '', trx['AMOUNT']))
#                     description = trx['DESCRIPTION'].replace('ELECTRONIC WITHDRAWAL', '')
#                     description = description.replace('ELECTRONIC DEPOSIT', '')
#                     description = description.strip(' -')
#                     transactions.append(Transaction(
#                         user=user,
#                         account_id=self.account.id,
#                         trxid=trx['trxid'],
#                         payee=description,
#                         amount=amount,
#                         date=date.date(),
#                         # original values
#                         original_date=date.date(),
#                         original_payee=description,
#                         original_amount=amount,
#                     ))
#                     # Newest transactions are first
#                     if balance is None:
#                         balance = Decimal(re.sub(r'[^\-*\d.]', '', trx['CURRENT BALANCE']))
#                         balancedt = date
#             self.label_transactions(transactions)
#             self.categorize_transactions(transactions)
#             log.info('Saving %s new transactions from qfx file: %s' % (len(transactions), filename))
#             Transaction.objects.bulk_create(transactions)
#             self.status.append('%s: added %s transactions' % (filename, len(transactions)))
#             self.transactions += len(transactions)
#             # Update account balance
#             if balancedt:
#                 statementdt = timezone.make_aware(balancedt)
#                 if self.account.balancedt is None or statementdt >= self.account.balancedt:
#                     self.account.balance = balance
#                     self.account.balancedt = statementdt
#                     self.account.save()
#         except Exception as err:
#             log.exception(err)
#             self.status.append('Error %s: %s' % (filename, err))

#     def import_qfx(self, user, filename, handle):
#         """ Import transactions from a qfx file. """
#         try:
#             self.files += 1
#             self.filename = filename
#             transactions = []
#             log.info('Importing transactions qfx file: %s' % filename)
#             qfx = OfxParser.parse(handle)
#             fid = int(qfx.account.institution.fid)
#             if fid not in self._accounts_by_fid:
#                 raise Exception('Not tracking account fid: %s' % fid)
#             self.account = self._accounts_by_fid[fid]
#             # Update transactions
#             for trx in qfx.account.statement.transactions:
#                 trx = trx.__dict__
#                 trx['trxid'] = trx['id']
#                 trx['accountfid'] = fid
#                 if not self._transaction_exists(trx, addit=True):
#                     transactions.append(Transaction(
#                         user=user,
#                         account_id=self.account.id,
#                         trxid=trx['id'],
#                         payee=trx[self.account.payee or 'payee'],
#                         amount=trx['amount'],
#                         date=trx['date'].date(),
#                         # original values
#                         original_date=trx['date'].date(),
#                         original_payee=trx[self.account.payee or 'payee'],
#                         original_amount=trx['amount'],
#                     ))
#             self.label_transactions(transactions)
#             self.categorize_transactions(transactions)
#             log.info('Saving %s new transactions from qfx file: %s' % (len(transactions), filename))
#             Transaction.objects.bulk_create(transactions)
#             self.status.append('%s: added %s transactions' % (filename, len(transactions)))
#             self.transactions += len(transactions)
#             # Update account balance
#             statementdt = timezone.make_aware(qfx.account.statement.end_date)
#             if self.account.balancedt is None or statementdt > self.account.balancedt:
#                 self.account.balance = qfx.account.statement.balance
#                 self.account.balancedt = statementdt
#                 self.account.save()
#         except Exception as err:
#             log.exception(err)
#             self.status.append('Error %s: %s' % (filename, err))

#     def label_transactions(self, transactions):
#         lastyear = datetime.datetime.now() - timedelta(days=370)
#         labels = Transaction.objects.filter(payee__startswith='<', date__gte=lastyear)
#         labels = dict(labels.values_list('payee','amount').order_by('date'))
#         lookup = dict((v,k) for k,v in labels.items())
#         for trx in transactions:
#             if not trx.payee and trx.amount in lookup:
#                 trx.payee = lookup[trx.amount]
#                 self.labeled += 1

#     def categorize_transactions(self, transactions, save=False):
#         # Get all categorized items from the last 24 months
#         # All Special chars found: /*,':-`&_.#
#         lastyear = datetime.datetime.now() - timedelta(days=740)
#         items = Transaction.objects.filter(date__gte=lastyear)
#         items = items.exclude(payee='').exclude(category=None)
#         items = items.values_list('payee', 'category__id').order_by('date')
#         # Create lookup dictionary of already categorized items
#         lookup = {clean_name(payee):catid for payee,catid in items}
#         # Attempt to categorize everything
#         for trx in transactions:
#             payee = clean_name(trx.payee)
#             if not trx.category_id and payee in lookup:
#                 trx.category_id = lookup[payee]
#                 self.categorized += 1
#                 if save: trx.save()
#         return self.categorized


# def clean_name(payee):
#     """ Clean the Payee string, removing crud that may differ between
#         transacations but still represent the same payee.
#     """
#     payee = ''.join([c for c in payee.upper() if c not in REMOVE])                # Remove bad chars
#     payee = ''.join([c if c in f'{CHARS}{NUMS}{KEEP}' else ' ' for c in payee])   # Replace special chars with space
#     payee = ' '.join([w for w in payee.split() if not _is_code(w)])               # Remove id codes
#     payee = ''.join([c for c in payee if c in f'{CHARS}{KEEP}'])                  # Remove all numbers
#     payee = ' '.join([w for w in payee.split() if not len(w) == 1])               # Remove 1 char words
#     return ' '.join(payee.split())


# def _is_code(word):
#     """ Return True if num-char-num or char-num-char word. """
#     currenttype = None      # current type of character (num or char)
#     switchcount = 0         # Number of times we switched types
#     for char in word:
#         ctype = 'char' if char in f'{CHARS}{KEEP}' else 'num'
#         if ctype != currenttype:
#             currenttype = ctype
#             switchcount += 1
#         if switchcount >= 3:
#             return True
#     return False
