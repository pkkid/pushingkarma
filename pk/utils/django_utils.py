# encoding: utf-8
import logging, re, requests, textwrap, time
from collections import defaultdict
from django.conf import settings
from django.db import connections
from django.db.models import Model, DateTimeField
from django.urls import reverse as django_reverse
from urllib.parse import unquote
from . import utils
log = logging.getLogger(__name__)


class ColoredFormatter(logging.Formatter):
    RELVL = r'%\(levelname\)\-7s'
    COLORS = {
        logging.DEBUG: '#555',
        logging.WARNING: '#D93',
        logging.ERROR: '#C21',
        logging.CRITICAL: '#F44',
    }
    
    def __init__(self, fmt=None, **kwargs):
        super().__init__(fmt, **kwargs)
        self._formatters = {}
        substr = re.findall(self.RELVL, fmt)[0]
        for lvl, color in self.COLORS.items():
            newfmt = fmt.replace(substr, utils.rgb(substr, color))
            self._formatters[lvl] = logging.Formatter(newfmt)

    def format(self, record):
        formatter = self._formatters.get(record.levelno, super())
        return formatter.format(record)
    

class QueryCounterMiddleware:
    DATACOLOR, REQCOLOR, SQLCOLOR = '#d93', '#b68', '#488'
    FIRST, LAST = utils.rgb('  ┌ ', REQCOLOR), utils.rgb('  └ ', REQCOLOR)
    BULLET, PIPE = utils.rgb('  ├ ', REQCOLOR), utils.rgb('  │ ', REQCOLOR)
    INDENTSTR = PIPE + utils.rgb('   ', '#488', reset=False)
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
        if log_enabled:
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
        logmsg += self.FIRST + utils.rgb(f'{request.method} {request.get_full_path()}', self.REQCOLOR) + '\n'
        for sql, sqldata in summary['queries'].items():
            sqlstr = self.BULLET + utils.rgb(f'[{sqldata["sqltime"]:.3f}s] ', self.DATACOLOR)
            if sqldata['count'] > 1:
                sqlstr = self.BULLET + utils.rgb(f'[{sqldata["count"]}x {sqldata["avgtime"]:.3f}s] ', self.DATACOLOR)
            sqlstr += utils.rgb(sql, self.SQLCOLOR)
            logmsg += textwrap.fill(sqlstr, width=160, subsequent_indent=self.INDENTSTR) + '\n'
        proctime = resptime - summary['sqltime']
        logmsg += self.BULLET + utils.rgb(f'Request took {resptime:.3f}s ({proctime:.3f}s processing)', self.DATACOLOR) + '\n'
        logmsg += self.LAST + utils.rgb(summarystr, self.DATACOLOR)
        log.info(logmsg)


# NOT SURE WHY I CANT PUT THIS HERE
# class TimeStampedModel(Model):
#     """ TimeStampedModel - An abstract base class model that provides self-managed
#         created and modified fields. Pulled from Django-Extentions.
#         https://github.com/django-extensions/django-extensions
#     """
#     created = DateTimeField(editable=False, blank=True, auto_now_add=True)
#     modified = DateTimeField(auto_now=True)

#     class Meta:
#         get_latest_by = 'modified'
#         abstract = True


def get_object_or_none(cls, *args, **kwargs):
    try:
        return cls._default_manager.get(*args, **kwargs)
    except cls.DoesNotExist:
        return None


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
        servername = utils.rget(request, 'environ.SERVER_NAME', 'localhost')
        serverurl = f'http://{servername}:5173'
        requests.head(serverurl)
        return serverurl
    except Exception:
        return None
