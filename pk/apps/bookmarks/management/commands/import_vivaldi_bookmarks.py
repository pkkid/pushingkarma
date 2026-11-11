# encoding: utf-8
"""
Replace a user's bookmarks with the bookmarks bar from a Vivaldi (or Chrome)
Bookmarks file. Favicons and other browser metadata are ignored.
"""
import json, logging, os
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from ...models import Bookmark, FOLDER, LINK, SEPARATOR
log = logging.getLogger(__name__)
DEFAULT_PATH = '~/.config/vivaldi/Default/Bookmarks'


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument('user', help='Username or email of user to import bookmarks for.')
        parser.add_argument('--path', default=DEFAULT_PATH, help=f'Bookmarks file (default: {DEFAULT_PATH})')

    @transaction.atomic
    def handle(self, *args, **opts):
        user = User.objects.get(Q(username=opts['user']) | Q(email=opts['user']))
        with open(os.path.expanduser(opts['path'])) as handle:
            bookmarkbar = json.load(handle)['roots']['bookmark_bar']
        Bookmark.objects.filter(user=user).delete()
        count = self.import_children(user, None, bookmarkbar.get('children', []))
        log.info(f'Imported {count} bookmarks for {user.username}')

    def import_children(self, user, parent, children):
        """ Recursively create bookmarks for children, returns the number created. """
        count = 0
        for sortid, node in enumerate(children):
            kind = FOLDER if node['type'] == 'folder' else LINK
            if node.get('meta_info', {}).get('Description') == 'separator':
                kind = SEPARATOR
            item = Bookmark.objects.create(user=user, parent=parent, kind=kind, sortid=sortid,
                title=node['name'] if kind != SEPARATOR else '', url=node.get('url', '') if kind == LINK else '')
            count += 1 + self.import_children(user, item, node.get('children', []))
        return count
