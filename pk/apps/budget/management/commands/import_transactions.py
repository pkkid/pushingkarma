# encoding: utf-8
# Import transactions from qfx file.
import logging, os
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from pk.utils.django import update_logging_filepath
from ...manager import TransactionManager
log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument('user', required=True, help='Email address of user to import for.')
        parser.add_argument('filepath', required=True, nargs='+', help='Transaction file(s) to import (.csv or .qfx)')
        parser.add_argument('safeimport', default=False, action='store_true', help='Unique trxs based on date, payee and amount.')
        parser.add_argument('--loglevel', default='INFO', help='Console log level')

    def handle(self, *args, **options):
        # Setup logging
        logging.getLogger().setLevel(self.opts['loglevel'])
        basename = os.path.basename(__file__).replace('.py', '')
        update_logging_filepath(f'{settings.LOGDIR}/{basename}.log')
        # Run the script
        user = User.objects.get(email=options['user'])
        trxmanager = TransactionManager(user, options['safeimport'], test=True)
        for filepath in options['filepath']:
            filename = os.path.basename(filepath)
            with open(filepath) as handle:
                metrics = trxmanager.import_file(filename, handle)
            log.info(metrics)
