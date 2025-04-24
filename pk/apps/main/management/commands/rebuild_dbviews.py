"""
Rebuild the Database Views
Manually rebuild the database views when a change is made.
"""
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from pk.utils.django import create_views_sql, drop_views_sql


class Command(BaseCommand):
    help = __doc__
    
    def handle(self, *args, **opts):
        with transaction.atomic():
            with connection.cursor() as cursor:
                for sql in drop_views_sql().split(';'):
                    cursor.execute(sql)
                for sql in create_views_sql().split(';'):
                    cursor.execute(sql)
