# encoding: utf-8
# Remove duplicate entries
from django.core.management.base import BaseCommand
from django.db.models import Count
from django.db.models import Aggregate, CharField
from pk.apps.user.models import User
from pk.apps.budget.models import Account, Transaction


class GroupConcat(Aggregate):
    function = 'GROUP_CONCAT'
    template = '%(function)s(%(distinct)s%(expressions)s)'

    def __init__(self, expression, distinct=False, **extra):
        super(GroupConcat, self).__init__(
            expression,
            distinct='DISTINCT ' if distinct else '',
            output_field=CharField(),
            **extra)


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument('user', help='Email address of user to remove duplicates for.')
        parser.add_argument('--update-trxids', type=bool, default=False, help='Update trxids for this account.')

    def _count_duplicates(self, user, account):
        """ Returns the count of duplicates. """
        trxs = Transaction.objects.filter(user=user, account=account)
        trxs = trxs.values('account', 'date', 'payee', 'amount')
        trxs = trxs.annotate(count=Count('*'), ids=GroupConcat('id'), trxids=GroupConcat('trxid'))
        trxs = trxs.filter(count__gte=2)
        return trxs.count()
    
    def _agree_to_proceed(self, options, user, account):
        """ Do we want to continue? Returns True if we should proceed. """
        count = self._count_duplicates(user, account)
        print(f'\nFound ~{count} duplicates on account {account.name}.')
        if count:
            print(f'Choosing to continue will {"" if options["update_trxids"] else "NOT"} update transaction ids.')
            return input('Would you like to continue? (y/N): ').lower() == 'y'
        return False

    def handle(self, *args, **options):
        # Check the number of duplicates we have to work with.
        user = User.objects.get(email=options['user'])
        account = Account.objects.get(id=options['accountid'])
        if not self._agree_to_proceed(options, user, account):
            raise SystemExit('Done.\n')
        # Get all transactions for the user and account
        trxs = Transaction.objects.filter(user=user, account=account)
        trxs = trxs.order_by('date', 'payee', 'amount')
        p, count = None, 0
        for c in trxs:
            if not p or not (p.date == c.date and p.payee.lower() == c.payee.lower() and p.amount == c.amount):
                p = c; continue
            count += 1
            print(f'{count}. Duplicate: {p.id}={c.id}; {p.date.strftime("%Y-%m-%d")}; {p.payee}; ${p.amount})')
            trxid = c.trxid; c.delete()
            p.trxid = trxid; p.save()
        print()
