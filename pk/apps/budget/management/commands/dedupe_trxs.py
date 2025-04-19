# encoding: utf-8
# Remove duplicate entries
import logging, os
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Count
from pk.utils.django import GroupConcat, update_logging_filepath
from pk.utils import utils
from ...models import Transaction
log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = __doc__

    def _get_duplicates(self, user, account_name):
        """ Returns the count of duplicates. """
        trxs = Transaction.objects.filter(user=user)
        if account_name:
            trxs = trxs.filter(account__name__iexact=account_name)
        trxs = trxs.exclude(comment__icontains='dupe-ok')
        trxs = trxs.values('account', 'date', 'payee', 'amount')
        trxs = trxs.annotate(count=Count('*'), ids=GroupConcat('id'), trxids=GroupConcat('trxid'))
        trxs = trxs.filter(count__gte=2)
        return trxs

    def _ask_what_to_do(self, i, dupe):
        """ Do we want to continue? Returns True if we should proceed. """
        result = None
        dtstr = dupe['date'].strftime('%Y-%m-%d')
        print(f'\n{i+1:>2}.) {dupe["count"]}x  {dupe["account"]}  {dtstr}  {dupe["payee"]}  {dupe["amount"]}  (ids: {dupe["ids"]})')
        while result not in ['ignore', 'clean', 'keep']:
            result = input(utils.rgb('     What would you like to do? (ignore, clean, keep): ', '#6aa')).lower()
        return result
    
    def _clean_duplicate(self, dupe):
        """ Clean up duplicates. """
        ids = dupe['ids'].split(',')
        log.info(f'Deleting transactions: {", ".join(ids[1:])}')
        Transaction.objects.filter(id__in=ids[1:]).delete()

    def _keep_duplicate(self, dupe):
        """ Keep the duplicates. """
        ids = dupe['ids'].split(',')
        log.info(f'Commenting dupe-ok for transactions: {", ".join(ids)}')
        for trx in Transaction.objects.filter(id__in=ids):
            trx.comment = f'{trx.comment} dupe-ok' if trx.comment else 'dupe-ok'
            trx.save()

    def add_arguments(self, parser):
        parser.add_argument('user', help='Email address of user to import for.')
        parser.add_argument('--account', help='Name of the financial account to dedupe.')
        parser.add_argument('--loglevel', default='INFO', help='Console log level')

    def handle(self, *args, **opts):
        try:
            # Setup logging
            logging.getLogger().setLevel(opts['loglevel'])
            basename = os.path.basename(__file__).replace('.py', '')
            update_logging_filepath(f'{settings.LOGDIR}/{basename}.log')
            # Run the script
            user = User.objects.get(email=opts['user'])
            dupes = self._get_duplicates(user, opts['account'])
            log.info(f'Found {dupes.count()} duplicates')
            for i, dupe in enumerate(dupes):
                result = self._ask_what_to_do(i, dupe)
                if result == 'clean': self._clean_duplicate(dupe)
                if result == 'keep': self._keep_duplicate(dupe)
        except KeyboardInterrupt:
            print()
        log.info('Done')
