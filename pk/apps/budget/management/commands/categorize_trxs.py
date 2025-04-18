# encoding: utf-8
# Categorize Transacations
import logging, os
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from pk.utils.django import update_logging_filepath
from ...manager import TransactionManager
from ...models import Account, Transaction
log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument('user', help='Email address of user to categorize transactions.')
        parser.add_argument('--loglevel', default='INFO', help='Console log level')

    def handle(self, *args, **opts):
        # Setup logging
        logging.getLogger().setLevel(opts['loglevel'])
        basename = os.path.basename(__file__).replace('.py', '')
        update_logging_filepath(f'{settings.LOGDIR}/{basename}.log')
        # Run the script
        user = User.objects.get(email=opts['user'])
        updated = []
        for account in Account.objects.filter(user=user):
            categories = TransactionManager.categories(account.user, account)
            for trx in Transaction.objects.filter(user=user, account=account, category=None):
                newcategoryid = categories.get(trx.payee.lower())
                if newcategoryid:
                    trx.category_id = newcategoryid
                    updated.append(trx)
        log.info(f'Updating category for {len(updated)} transactions')
        log.info('Done')
