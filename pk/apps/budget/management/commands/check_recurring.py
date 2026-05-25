# encoding: utf-8
"""Run recurring detection against the local database with an optional search filter."""
import logging
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from pk.apps.budget.api import TRANSACTIONSEARCHFIELDS
from pk.apps.budget.recurring import RecurringManager


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument('--search', default='', help='Budget search query to filter transactions')
        parser.add_argument('--showinactive', action='store_true', help='Include inactive recurring items')
        parser.add_argument('--user', default='', help='User email (defaults to first user)')
        parser.add_argument('--limit', type=int, default=0, help='Limit number of printed items (0 = no limit)')
        parser.add_argument('--loglevel', default='INFO', help='Console log level')

    def handle(self, *args, **opts):
        logging.getLogger().setLevel(opts['loglevel'])
        usermodel = get_user_model()
        user = usermodel.objects.filter(email=opts['user']).first() if opts['user'] else usermodel.objects.first()
        if not user:
            raise CommandError('No user found. Provide --user with a valid email.')
        manager = RecurringManager(user, search=opts['search'], searchfields=TRANSACTIONSEARCHFIELDS)
        items = manager.items if opts['showinactive'] else [item for item in manager.items if item.is_active]
        if opts['limit'] > 0:
            items = items[:opts['limit']]
        self.stdout.write(
            f'user={user.email} search="{opts["search"]}" '
            f'showinactive={opts["showinactive"]} recurring_count={len(items)}'
        )
        for item in items:
            out = f'- {item.name} | {item.cadence} | count={item.count}'
            out += f' | {item.first_date}..{item.last_date} | avg={item.average}'
            if not item.is_active:
                out += ' | inactive'
            if item.latest_comment:
                out += f' | comment={item.latest_comment}'
            self.stdout.write(out)
