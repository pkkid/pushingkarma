#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.

References:
https://github.com/jseutter/ofxparse
https://console.developers.google.com/
"""
import datetime
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from ofxparse import OfxParser
from pk import log
from pk.utils.decorators import lazyproperty
from .models import Account, Transaction

TRXJUNK = '#0123456789 '


class TransactionManager:

    def __init__(self):
        self.status = []            # status msg per file
        self.errors = 0             # num errors encoundered
        self.files = 0              # num files imported
        self.transactions = 0       # num transactions imported
        self.categorized = 0        # num transactions categorized
        self.labeled = 0            # num transactions labeled

    def get_status(self):
        return {
            'files': self.files,
            'transactions': self.transactions,
            'categorized': self.categorized,
            'labeled': self.labeled,
            'status': '\n'.join(self.status),
        }

    @lazyproperty
    def _accounts(self):
        return {a.fid:a for a in Account.objects.all()}

    @lazyproperty
    def _existing(self):
        existing = Transaction.objects.order_by('-date')
        return existing.values('account__fid','trxid','payee','category__name','amount')

    @lazyproperty
    def _existing_ids(self):
        return set((trx['account__fid'], trx['trxid']) for trx in self._existing)

    @lazyproperty
    def _existing_categories(self):
        return {trx['payee'].lower().rstrip('0123456789 '):trx['category__name']
            for trx in self._existing if trx['payee'] and trx['category__name']}

    def _transaction_exists(self, trx, addit=False):
        result = (int(trx['accountfid']), trx['trxid']) in self._existing_ids
        if result is False and addit is True:
            self._lazy__existing_ids.add((int(trx['accountfid']), trx['trxid']))
        return result

    def import_qfx(self, filename, handle):
        """ Import transactions from a qfx file. """
        try:
            self.files += 1
            transactions = []
            log.info('Importing transactions qfx file: %s' % filename)
            qfx = OfxParser.parse(handle)
            fid = int(qfx.account.institution.fid)
            if fid not in self._accounts:
                raise Exception('Not tracking account fid: %s' % fid)
            account = self._accounts[fid]
            # Update transactions
            trx_maxdate = None
            for trx in qfx.account.statement.transactions:
                trx = trx.__dict__
                trx['trxid'] = trx['id']
                trx['accountfid'] = fid
                if not self._transaction_exists(trx, addit=True):
                    transactions.append(Transaction(
                        account_id=account.id,
                        trxid=trx['id'],
                        payee=trx[account.payee or 'payee'],
                        amount=trx['amount'],
                        date=trx['date'].date(),
                    ))
            self.label_transactions(transactions)
            self.categorize_transactions(transactions)
            log.info('Saving %s new transactions from qfx file: %s' % (len(transactions), filename))
            Transaction.objects.bulk_create(transactions)
            self.status.append('%s: added %s transactions' % (filename, len(transactions)))
            self.transactions += len(transactions)
            # Update account balance
            statementdt = timezone.make_aware(qfx.account.statement.end_date)
            if account.balancedt is None or statementdt > account.balancedt:
                account.balance = qfx.account.statement.balance
                account.balancedt = statementdt
                account.save()
        except Exception as err:
            log.exception(err)
            self.status.append('Error %s: %s' % (filename, err))

    def label_transactions(self, transactions):
        lastyear = datetime.datetime.now() - relativedelta(months=13)
        labels = Transaction.objects.filter(payee__startswith='<', date__gte=lastyear)
        labels = dict(labels.values_list('payee','amount').order_by('date'))
        lookup = dict((v,k) for k,v in labels.items())
        for trx in transactions:
            if not trx.payee and trx.amount in lookup:
                trx.payee = lookup[trx.amount]
                self.labeled += 1

    def categorize_transactions(self, transactions):
        lastyear = datetime.datetime.now() - relativedelta(months=13)
        items = Transaction.objects.filter(date__gte=lastyear).exclude(payee='')
        items = items.values_list('payee', 'category__id').order_by('date')
        lookup = {payee.lower().rstrip(TRXJUNK):catid for payee,catid in items}
        for trx in transactions:
            payee = trx.payee.lower().rstrip(TRXJUNK)
            if not trx.category and payee in lookup:
                trx.category_id = lookup[payee]
                self.categorized += 1
