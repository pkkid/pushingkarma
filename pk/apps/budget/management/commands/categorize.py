# encoding: utf-8
# Categorize Transacations
from django.core.management.base import BaseCommand
from pk.apps.user.models import User
from ...manager import TransactionManager
from ...models import Transaction


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument('user', help='Email address of user to import for.')

    def handle(self, *args, **options):
        trxmanager = TransactionManager()
        user = User.objects.get(email=options['user'])
        uncategorized = Transaction.objects.filter(user=user, category=None)
        trxmanager.categorize_transactions(uncategorized, save=True)
