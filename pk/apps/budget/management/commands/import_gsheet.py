#!/usr/bin/env python
# encoding: utf-8
"""
Import transactions from Google Spreadsheet.
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from django.core.management.base import BaseCommand
from ...manager import TransactionManager


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument('url', help='URL of the spreadsheet to open.')
        parser.add_argument('--sheet', help='Name of the sheet to open (default first tab).')
        parser.add_argument('--head', type=int, default=1, help='Num worksheet header rows (default=1).')

    def handle(self, *args, **options):
        trxmanager = TransactionManager()
        trxmanager.import_gsheet(options['url'], options['sheet'], options['head'])
