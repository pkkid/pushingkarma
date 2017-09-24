#!/usr/bin/env python
# encoding: utf-8
"""
Import transactions from Google Spreadsheet.
Copyright (c) 2015 PushingKarma. All rights reserved.

https://console.developers.google.com/
https://pygsheets.readthedocs.io/en/latest/authorizing.html
"""
import datetime, os, pygsheets
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from pk.apps.budget.models import Category, Transaction

GSHEETS_CREDSTORE = getattr(settings, 'GSHEETS_CREDSTORE', None)
GSHEETS_SECRETS = getattr(settings, 'GSHEETS_SECRETS', None)


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument('url', help='URL of the spreadsheet to open.')
        parser.add_argument('--sheet', help='Name of the sheet to open (default first tab).')
        parser.add_argument('--header', type=int, default=1, help='Worksheet header row (default=1).')
        parser.add_argument('--credstore', help='Path to Google Sheets cred store dir.', default=GSHEETS_CREDSTORE)
        parser.add_argument('--secrets', help='Path to Google Sheets secrets file.', default=GSHEETS_SECRETS)

    def log(self, msg):
        datestr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.stdout.write('%s %s' % (datestr, msg))

    def get_gsheets_client(self, options):
        self.log('Connecting to Google Sheets')
        secrets = os.path.expanduser(options['secrets'])
        credstore = os.path.expanduser(options['credstore'])
        return pygsheets.authorize(secrets, outh_creds_store=credstore)

    def import_transactions(self, sheet, options):
        transactions = []
        categories = {k.lower():v for k,v in Category.objects.values_list('name', 'id')}
        self.log('Loading existing transactions from sheet: %s' % sheet.title)
        for trx in sheet.get_all_records(head=options['header']):
            transaction = Transaction(bankid=trx['ID'], account=trx['Account'],
                date=trx['Date'], payee=trx['Payee'], amount=trx['Amount'])
            if 'Memo' in trx: transaction.memo = trx['Memo']
            if 'Comment' in trx: transaction.comment = trx['Comment']
            if 'Category' in trx: transaction.category_id = categories[trx['Category'].lower()]
            if 'X' in trx: transaction.approved = trx['X'] == 'x'
            transactions.append(transaction)
        return transactions

    def handle(self, *args, **options):
        self.log('Importing transactions from spreadsheet')
        if not options['credstore']: raise CommandError('--credstore not specified.')
        if not options['secrets']: raise CommandError('--secrets not specified.')
        client = self.get_gsheets_client(options)
        spreadsheet = client.open_by_url(options['url'])
        sheet = spreadsheet.worksheet_by_title(options['sheet']) if options['sheet'] else spreadsheet.sheet1
        transactions = self.import_transactions(sheet, options)
