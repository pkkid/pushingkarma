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
from django.conf import settings
from ofxparse import OfxParser
from pk import log
from pk.utils.decorators import lazyproperty
from .models import Account, Transaction

GSHEETS_CREDSTORE = getattr(settings, 'BUDGET_GSHEETS_CREDSTORE', None)
GSHEETS_SECRETS = getattr(settings, 'BUDGET_GSHEETS_SECRETS', None)
TRXJUNK = '#0123456789 '


class TransactionManager:

    def __init__(self):
        self.status = []

    @lazyproperty
    def _accounts(self):
        return {a['fid']:a for a in Account.objects.all()}

    @lazyproperty
    def _existing(self):
        existing = Transaction.objects.order_by('-date')
        return existing.values('account__fid','trxid','payee','category__name','amount')

    @lazyproperty
    def _existing_ids(self):
        return set((trx['account__fid'], trx['trxid']) for trx in self._existing)

    @lazyproperty
    def _existing_labels(self):
        return set((trx['account__fid'], trx['amount'])
            for trx in self._existing if trx['payee'].startswith('<'))

    @lazyproperty
    def _existing_categories(self):
        return {trx['payee'].lower().rstrip('0123456789 '):trx['category__name']
            for trx in self._existing if trx['payee'] and trx['category__name']}

    def _transaction_exists(self, trx, addit=False):
        result = (int(trx['account__fid']), trx['trxid']) in self._existing_ids
        if result is False and addit is True:
            self._lazy__existing_ids.add((int(trx['account__fid']), trx['trxid']))
        return result

    def import_qfx(self, filename, handle):
        """ Import transactions from a qfx file. """
        try:
            log.info('Importing transactions qfx file: %s' % filename)
            transactions = []
            qfx = OfxParser.parse(handle)
            if qfx.account.institution.fid not in self._accounts:
                raise Exception('Not tracking account fid.')
            account = self._accounts[qfx.account.institution.fid]
            for trx in qfx.account.statement.transactions:
                trx = trx.__dict__
                trx['trxid'] = trx['id']
                if not self._transaction_exists(trx, addit=True):
                    transactions.append(Transaction(
                        account_id=account.id,
                        trxid=trx['id'],
                        payee=trx[account.get('payee', 'payee')],
                        amount=trx['amount'],
                        date=trx['date'].date(),
                    ))
            self.label_transactions(transactions)
            self.categorize_transactions(transactions)
            log.info('Saving %s new transactions from qfx file: %s' % (len(transactions), filename))
            Transaction.objects.bulk_create(transactions)
            self.status.append('%s: added %s transactions' % (filename, len(transactions)))
        except Exception as err:
            log.exception(err)
            self.status.append('%s: %s' % (filename, err))

    def label_transactions(self, transactions):
        lastyear = datetime.datetime.now() - relativedelta(months=13)
        labels = Transaction.objects.filter(payee__startswith='<', date__gte=lastyear)
        labels = dict(labels.values_list('payee','amount').order_by('date'))
        lookup = dict((v,k) for k,v in labels.items())
        for trx in transactions:
            if not trx.payee and trx.amount in lookup:
                trx.payee = lookup[trx.amount]

    def categorize_transactions(self, transactions):
        lastyear = datetime.datetime.now() - relativedelta(months=13)
        items = Transaction.objects.filter(date__gte=lastyear).exclude(payee='')
        items = items.values_list('payee', 'category__id').order_by('date')
        lookup = {payee.lower().rstrip(TRXJUNK):catid for payee,catid in items}
        for trx in transactions:
            payee = trx.payee.lower().rstrip(TRXJUNK)
            if not trx.category and payee in lookup:
                trx.category_id = lookup[payee]
