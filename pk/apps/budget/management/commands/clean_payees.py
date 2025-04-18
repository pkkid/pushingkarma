# encoding: utf-8
# Import transactions from qfx file.
import logging, os
from django.conf import settings
from django.core.management.base import BaseCommand
from pk.utils.django import update_logging_filepath
from ...manager import TransactionManager
from ...models import Transaction
log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument('--loglevel', default='INFO', help='Console log level')

    def handle(self, *args, **opts):
        # Setup logging
        logging.getLogger().setLevel(opts['loglevel'])
        basename = os.path.basename(__file__).replace('.py', '')
        update_logging_filepath(f'{settings.LOGDIR}/{basename}.log')
        # Run the script
        updated = []
        for trx in Transaction.objects.all():
            newpayee = TransactionManager.clean_payee(trx.payee)
            if trx.payee != newpayee:
                log.info(f'  "{trx.payee}" -> "{newpayee}"')
                trx.payee = newpayee
                updated.append(trx)
        log.info(f'Cleaning payee for {len(updated)} transactions')
        log.info('Done')
