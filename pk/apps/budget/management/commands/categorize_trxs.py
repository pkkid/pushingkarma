# encoding: utf-8
# Categorize Transacations
import logging, os
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from pk.utils.django import update_logging_filepath
from ...trxmanager import TransactionManager
from ...models import Account, Transaction
log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument('user', help='Email address of user to categorize transactions.')
        parser.add_argument('--save', default=False, action='store_true', help='Save changes')
        parser.add_argument('--loglevel', default='INFO', help='Console log level')

    def handle(self, *args, **opts):
        # Setup logging
        logging.getLogger().setLevel(opts['loglevel'])
        basename = os.path.basename(__file__).replace('.py', '')
        update_logging_filepath(f'{settings.LOGDIR}/{basename}.log')
        # Run the script
        updated = []
        user = User.objects.get(email=opts['user'])
        for account in Account.objects.filter(user=user):
            payee_categoryids = TransactionManager.payee_categoryids(account.user, account)
            for trx in Transaction.objects.filter(user=user, account=account, category=None):
                catpayee = TransactionManager.scrub_payee(trx.payee)
                newcategoryid = payee_categoryids.get(catpayee)
                if newcategoryid:
                    log.info(f'  {trx.payee} -> {newcategoryid}')
                    trx.category_id = newcategoryid
                    updated.append(trx)
        log.info(f'Updating category for {len(updated)} transactions')
        if opts['save']:
            Transaction.objects.bulk_update(updated, ['category'])
        log.info(f'Done {"" if opts["save"] else "(without saving!)"}')
