# encoding: utf-8
import logging, re, sqlparse
from django.core.exceptions import EmptyResultSet
from django.db import connection
from django.db.models.query import QuerySet
log = logging.getLogger(__name__)


def queryset_str(sql_or_queryset):
    """ Return the raw sql of a queryset. It includes quotes! """
    try:
        sql = sql_or_queryset
        if isinstance(sql, QuerySet):
            sql, params = sql.query.sql_with_params()
            with connection.cursor() as cursor:
                cursor.execute(f'EXPLAIN {sql}', params)
                sql = cursor.db.ops.last_executed_query(cursor, sql, params)
        sql = re.sub('SELECT (.+?) FROM', 'SELECT * FROM', sql)
        sql = sqlparse.format(sql, reindent=True)
        sql = sql.replace('SELECT *\nFROM', 'SELECT * FROM')
        sql = sql.replace(' OR ', '\n  OR ')
        sql = sql.replace(' AND ', '\n  AND ')
        sql = re.sub(r'COUNT\(CASE\s+WHEN', '\n  COUNT(CASE WHEN', sql)
        sql = re.sub(r'THEN 1\s+ELSE NULL\s+END', 'THEN 1 ELSE NULL END', sql)
        sql = '\n'.join([x for x in sql.split('\n') if x.strip()])
        result, indent = [], 0
        for line in sql.split('\n'):
            line = f'  {line.strip()}' if line.startswith('  ') else line.strip()
            result.append(f'{" "*indent}{line}')
            indent = indent + line.count('(') - line.count(')')
        return '\n'.join(result) + ';'
    except EmptyResultSet:
        return 'EmptyResultSet'
