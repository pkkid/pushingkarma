#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.

References:
https://github.com/jseutter/ofxparse
https://console.developers.google.com/
https://pygsheets.readthedocs.io/en/latest/authorizing.html
"""
import pygsheets
from django.conf import settings
from ofxparse import OfxParser
from pk import log
from pk.utils.decorators import lazyproperty
from .models import Category, Transaction

ACCOUNTS = settings.BUDGET_ACCOUNTS
GSHEETS_CREDSTORE = getattr(settings, 'BUDGET_GSHEETS_CREDSTORE', None)
GSHEETS_SECRETS = getattr(settings, 'BUDGET_GSHEETS_SECRETS', None)


class TransactionManager:

    def __init__(self):
        self.status = []

    @lazyproperty
    def _existing(self):
        existing = Transaction.objects.order_by('-date')
        return existing.values('accountfid','trxid','payee','category__name','amount')

    @lazyproperty
    def _existing_ids(self):
        return set((trx['accountfid'], trx['trxid']) for trx in self._existing)

    @lazyproperty
    def _existing_labels(self):
        return set((trx['accountfid'], trx['amount'])
            for trx in self._existing if trx['payee'].startswith('<'))

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
            log.info('Importing transactions qfx file: %s' % filename)
            transactions = []
            qfx = OfxParser.parse(handle)
            if qfx.account.institution.fid not in ACCOUNTS:
                raise Exception('Not tracking account fid.')
            account = ACCOUNTS[qfx.account.institution.fid]
            for trx in qfx.account.statement.transactions:
                trx = trx.__dict__
                trx['accountfid'] = qfx.account.institution.fid
                trx['trxid'] = trx['id']
                if not self._transaction_exists(trx, addit=True):
                    transactions.append(Transaction(
                        account=account['name'],
                        accountfid=qfx.account.institution.fid,
                        trxid=trx['id'],
                        payee=trx[account.get('payee', 'payee')],
                        amount=trx['amount'],
                        date=trx['date'].date(),
                    ))
            log.info('Saving %s new transactions from qfx file: %s' % (len(transactions), filename))
            Transaction.objects.bulk_create(transactions)
            self.status.append('%s: added %s transactions' % (filename, len(transactions)))
        except Exception as err:
            log.exception(err)
            self.status.append('%s: %s' % (filename, err))
            
    def import_gsheet(self, url, sheet=None, head=1):
        """ Import transactions from a google spreadsheet. """
        try:
            transactions = []
            categories_not_found = set()
            client = pygsheets.authorize(GSHEETS_SECRETS, outh_creds_store=GSHEETS_CREDSTORE)
            spreadsheet = client.open_by_url(url)
            log.info('Importing transactions from Google spreadsheet: %s' % spreadsheet.title)
            sheet = spreadsheet.worksheet_by_title(sheet) if sheet else spreadsheet.sheet1
            categories = {name.lower():id for name,id in Category.objects.values_list('name','id')}
            for trx in sheet.get_all_records(head=head):
                trx = {k.lower():v for k,v in trx.items()}
                if not self._transaction_exists(trx, addit=True):
                    transactions.append(Transaction(
                        account=trx['account'],
                        accountfid=trx['accountfid'],
                        trxid=trx['trxid'],
                        payee=trx['payee'],
                        category_id=categories.get(trx['category'].lower(), None),
                        amount=trx['amount'].replace('$','').replace(',',''),
                        date=trx['date'],
                        approved=trx.get('approved',trx.get('x','')).lower() in ['x','t','true'],
                        memo=trx.get('memo',''),
                        comment=trx.get('comment',''),
                    ))
                    if not transactions[-1].category and trx['category'] not in categories_not_found:
                        log.warning("No category found for '%s'" % trx['category'])
                        categories_not_found.add(trx['category'])
            log.info('Saving %s new transactions from Google spreadsheet: %s' % (len(transactions), spreadsheet.title))
            Transaction.objects.bulk_create(transactions)
            self.status.append('%s: added %s transactions' % (spreadsheet.title, len(transactions)))
        except Exception as err:
            log.exception(err)
            self.status.append('%s: %s' % (url, err))

    def label_transactions(self):
        pass

    def categorize_transactions(self):
        pass
