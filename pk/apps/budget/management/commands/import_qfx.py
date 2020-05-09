# encoding: utf-8
# Import transactions from qfx file.
import os
from django.core.management.base import BaseCommand
from pk.apps.user.models import User
from ...manager import TransactionManager


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument('filepath', help='Path of qfx file to open.')
        parser.add_argument('user', help='Email address of user to import for.')

    def handle(self, *args, **options):
        filename = os.path.basename(options['filepath'])
        user = User.objects.get(email=options['user'])
        with open(options['filepath']) as handle:
            trxmanager = TransactionManager()
            trxmanager.import_qfx(user, filename, handle)
