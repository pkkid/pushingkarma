# encoding: utf-8
# Remove duplicate entries
import logging, os
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Count
from pk.utils.django import GroupConcat, update_logging_filepath
from ...models import Account, Transaction
log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = __doc__

    def _get_duplicates(self, user, account):
        """ Returns the count of duplicates. """
        trxs = Transaction.objects.filter(user=user, account=account)
        trxs = trxs.values('account', 'date', 'payee', 'amount')
        trxs = trxs.annotate(count=Count('*'), ids=GroupConcat('id'), trxids=GroupConcat('trxid'))
        trxs = trxs.filter(count__gte=2)
        return trxs

    def _agree_to_proceed(self, dupes, account):
        """ Do we want to continue? Returns True if we should proceed. """
        count = dupes.count()
        log.info(f'Found {count} duplicates on account {account.name}:')
        for dupe in dupes:
            dtstr = dupe['date'].strftime('%Y-%m-%d')
            log.info(f'  {dupe["count"]}x  {dtstr}  {dupe["payee"]:30.30}  {dupe["amount"]:>8}')
        return input('\nWould you like to continue? (y/N): ').lower() == 'y' if count else False

    def add_arguments(self, parser):
        parser.add_argument('user', help='Email address of user to import for.')
        parser.add_argument('account', help='Name of the financial account to dedupe.')
        parser.add_argument('--loglevel', default='INFO', help='Console log level')

    def handle(self, *args, **opts):
        # Setup logging
        logging.getLogger().setLevel(opts['loglevel'])
        basename = os.path.basename(__file__).replace('.py', '')
        update_logging_filepath(f'{settings.LOGDIR}/{basename}.log')
        # Run the script
        user = User.objects.get(email=opts['user'])
        account = Account.objects.get(user=user, name__iexact=opts['account'])
        dupes = self._get_duplicates(user, account)
        agreed = self._agree_to_proceed(dupes, account)
        log.info('Done')
