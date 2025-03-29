# encoding: utf-8
import logging, re, requests
import sqlparse, textwrap, time
from collections import defaultdict
from django.conf import settings
from django.core.exceptions import EmptyResultSet
from django.db import connection, connections
from django.db.models.query import QuerySet
from django.db.models import Model, DateTimeField
from django.urls import reverse as django_reverse
from urllib.parse import unquote
log = logging.getLogger(__name__)


def rgb(text, color='#aaa', reset=True):
    r,g,b = tuple(int(x * 2, 16) for x in color.lstrip('#'))
    rgbstr = f'\033[38;2;{r};{g};{b}m{text}'
    rgbstr += '\033[00m' if reset else ''
    return rgbstr


class QueryCounterMiddleware:
    DATACOLOR, REQCOLOR, SQLCOLOR = '#d93', '#b68', '#488'
    FIRST, LAST = rgb('  ┌ ', REQCOLOR), rgb('  └ ', REQCOLOR)
    BULLET, PIPE = rgb('  ├ ', REQCOLOR), rgb('  │ ', REQCOLOR)
    INDENTSTR = PIPE + rgb('   ', '#488', reset=False)
    REGEX_WHERE = re.compile(r'(\s+WHERE\s+)(.*)(\s+(?:GROUP|ORDER|HAVING)\s+)*')
    REGEX_VALUE = re.compile(r'(\s*[a-zA-Z_."]+?(?:_id|\."id)"\s*=\s*)\d+(\s*)')

    def __init__(self, get_response):
        self.get_response = get_response
        
    def _count_enabled(self, request):
        count_header = request.headers.get('Count-Queries', '').lower() == 'true'
        return settings.QUERYCOUNTER_ENABLE_HEADERS or count_header
    
    def _log_enabled(self, request):
        count_header = request.headers.get('Log-Queries', '').lower() == 'true'
        return settings.QUERYCOUNTER_ENABLE_LOG or count_header
    
    def __call__(self, request):
        """ Main middleware function, wraps the request. """
        # Check what we have enabled
        count_enabled = self._count_enabled(request)
        log_enabled = self._log_enabled(request)
        if not count_enabled and not log_enabled:
            return self.get_response(request)
        # Track connection.queries
        starttime = time.time()
        response = self.get_response(request)
        summary, summarystr = self._summarize_queries()
        resptime = time.time() - starttime
        # Log the summary and return the header
        if log_enabled and summary['count']:
            self._log_summary(request, resptime, summary, summarystr)
        if count_enabled:
            response['Response-Time'] = f'{resptime:.3f}s'
            response['Queries'] = summarystr
        return response

    def _summarize_queries(self):
        """ Summarizes the queries and merges duplicates. """
        summary = dict(count=0, sqltime=0,
            queries=defaultdict(lambda: dict(count=0, sqltime=0)))
        for conn in connections.all():
            for query in conn.queries:
                if sql := query.get('sql'):
                    sql = self._clean_sql(sql)
                    sqltime = float(query['time'].strip('[s]'))
                    summary['count'] += 1
                    summary['sqltime'] += sqltime
                    summary['queries'][sql]['count'] += 1
                    summary['queries'][sql]['sqltime'] += sqltime
        for sql, sqldata in summary['queries'].items():
            sqldata['avgtime'] = round(sqldata['sqltime'] / sqldata['count'], 3)
        summarystr = f'{summary["count"]} queries took {summary["sqltime"]:.3f}s'
        if duplicate := sum(q['count'] - 1 for q in summary['queries'].values()):
            summarystr += f' ({duplicate} duplicate)'
        return summary, summarystr
    
    def _clean_sql(self, sql):
        """ Cleans up the sql query for logging. """
        if settings.QUERYCOUNTER_SIMPLIFY_SQL:
            sql = re.sub('SELECT (.+?) FROM', 'SELECT * FROM', sql)
        if where := self.REGEX_WHERE.search(sql):
            values = self.REGEX_VALUE.sub(r'\1<val>\2', where.group(2))
            repl = 'r\1{}\3' if where.group(3) else r'\1{}'
            sql = self.REGEX_WHERE.sub(repl.format(values), sql)
        return sql
    
    def _log_summary(self, request, resptime, summary, summarystr):
        """ Logs the queries to the logger. """
        logmsg = f'QueryCounter tracked {summary["count"]} sql statements\n'
        logmsg += self.FIRST + rgb(f'{request.method} {request.get_full_path()}', self.REQCOLOR) + '\n'
        for sql, sqldata in summary['queries'].items():
            sqlstr = self.BULLET + rgb(f'[{sqldata["sqltime"]:.3f}s] ', self.DATACOLOR)
            if sqldata['count'] > 1:
                sqlstr = self.BULLET + rgb(f'[{sqldata["count"]}x {sqldata["avgtime"]:.3f}s] ', self.DATACOLOR)
            sqlstr += rgb(sql, self.SQLCOLOR)
            logmsg += textwrap.fill(sqlstr, width=160, subsequent_indent=self.INDENTSTR) + '\n'
        proctime = resptime - summary['sqltime']
        logmsg += self.BULLET + rgb(f'Request took {resptime:.3f}s ({proctime:.3f}s processing)', self.DATACOLOR) + '\n'
        logmsg += self.LAST + rgb(summarystr, self.DATACOLOR)
        log.info(logmsg)


class TimeStampedModel(Model):
    """ TimeStampedModel - An abstract base class model that provides self-managed
        created and modified fields. Pulled from Django-Extentions.
        https://github.com/django-extensions/django-extensions
    """
    created = DateTimeField(editable=False, blank=True, auto_now_add=True)
    modified = DateTimeField(auto_now=True)

    class Meta:
        get_latest_by = 'modified'
        abstract = True


def get_object_or_none(cls, *args, **kwargs):
    try:
        return cls._default_manager.get(*args, **kwargs)
    except cls.DoesNotExist:
        return None


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


def reverse(request, viewname, **kwargs):
    return unquote(request.build_absolute_uri(django_reverse(viewname, kwargs=kwargs)))


def update_logging_filepath(filepath, handler_name='default'):
    """ Update logging filehandler to the specified filepath. """
    for handler in logging.getLogger().handlers:
        if handler._name == handler_name and isinstance(handler, logging.FileHandler):
            handler.close()
            handler.baseFilename = filepath
            handler.stream = handler._open()
            break
    else:
        raise Exception(f'Unknown filehandler name {handler_name}')


def vue_devserver_running(request):
    """ Return url if it looks like the Vue devserver is running. """
    try:
        if not settings.DEBUG: return None
        servername = request['environ'].get('SERVER_NAME', 'localhost')
        serverurl = f'http://{servername}:5173'
        requests.head(serverurl)
        return serverurl
    except Exception:
        return None
