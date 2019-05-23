# encoding: utf-8
# Import transactions from qfx file.
import os
from django.core.management.base import BaseCommand
from ...manager import TransactionManager


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument('filepath', help='Path of qfx file to open.')

    def handle(self, *args, **options):
        filename = os.path.basename(options['filepath'])
        with open(options['filepath']) as handle:
            trxmanager = TransactionManager()
            trxmanager.import_qfx(filename, handle)
