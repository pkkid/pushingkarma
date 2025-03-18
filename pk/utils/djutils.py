# encoding: utf-8
import logging, re, textwrap, time
from django.conf import settings
from django.db import connection
from pk import utils
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

    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        if not settings.QUERYCOUNTER_ENABLED:
            return self.get_response(request)
        # Track connection.queries
        initqueries = len(connection.queries)
        starttime = time.time()
        response = self.get_response(request)
        numqueries = len(connection.queries) - initqueries
        resptime = time.time() - starttime
        # Start logging and add time of all queries
        sqltime, longest, logmsg = 0.0, 0.0, ''
        log_header = request.headers.get('Log-Queries', '').lower() == 'true'
        log_enabled = settings.QUERYCOUNTER_ENABLE_LOG or log_header
        if log_enabled:
            logmsg += self.FIRST + utils.rgb(f'{request.method} {request.get_full_path()}', '#b68') + '\n'
        for query in connection.queries[initqueries:]:
            querytime = float(query['time'].strip('[]s'))
            sqltime += querytime
            longest = max(longest, querytime)
            if log_enabled:
                _logstr = self.BULLET + utils.rgb(f'[{querytime:.3f}s] ', '#d93')
                _logstr += utils.rgb(query['sql'], '#488')
                logmsg += textwrap.fill(_logstr, width=160, subsequent_indent=self.INDENTSTR) + '\n'
        proctime = resptime - sqltime
        rsummary = f'Request took {resptime:.3f}s ({proctime:.3f}s processing)'
        qsummary = f'{numqueries} queries took {sqltime:.3f}s (longest {longest:.3f}s)'
        if log_enabled and numqueries:
            logmsg += self.BULLET + utils.rgb(rsummary, '#d93') + '\n'
            logmsg += self.LAST + utils.rgb(qsummary, '#d93')
            log.info(f'QueryCounter tracked {numqueries} sql statements\n' + logmsg)
        if settings.QUERYCOUNTER_ENABLE_HEADERS:
            response['Response-Time'] = f'{resptime:.3f}s'
            response['Queries'] = qsummary
        return response


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
