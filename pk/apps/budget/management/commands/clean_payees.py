# encoding: utf-8
# Import transactions from qfx file.
import logging, os
from django.conf import settings
from django.core.management.base import BaseCommand
from pk.utils.django import update_logging_filepath
from ...trxmanager import TransactionManager
from ...models import Transaction
log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument('--original', default=False, action='store_true', help='Save changes')
        parser.add_argument('--save', default=False, action='store_true', help='Save changes')
        parser.add_argument('--loglevel', default='INFO', help='Console log level')

    def handle(self, *args, **opts):
        # Setup logging
        logging.getLogger().setLevel(opts['loglevel'])
        basename = os.path.basename(__file__).replace('.py', '')
        update_logging_filepath(f'{settings.LOGDIR}/{basename}.log')
        # Run the script
        updated = []
        for trx in Transaction.objects.all():
            if opts['original']:
                neworiginal = TransactionManager.clean_payee(trx.original_payee)
                if trx.original_payee != neworiginal:
                    log.info(f'  "{trx.original_payee}" -> "{neworiginal}"')
                    trx.original_payee = neworiginal
                    updated.append(trx)
            else:
                newpayee = TransactionManager.clean_payee(trx.payee)
                if trx.payee != newpayee:
                    log.info(f'  "{trx.payee}" -> "{newpayee}"')
                    trx.payee = newpayee
                    updated.append(trx)
        origtext = "original" if opts["original"] else ""
        log.info(f'Cleaning {origtext} payee for {len(updated)} transactions')
        if opts['original'] and opts['save']:
            Transaction.objects.bulk_update(updated, ['payee', 'original_payee'])
        log.info(f'Done {"" if opts["save"] else "(without saving!)"}')
