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
    FIRST, LAST = utils.rgb('┌ ', REQCOLOR), utils.rgb('└ ', REQCOLOR)
    BULLET, PIPE = utils.rgb('├ ', REQCOLOR), utils.rgb('│ ', REQCOLOR)
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
        runtime = time.time() - starttime
        # Start logging and add time of all queries
        sqltime, longest = 0.0, 0.0
        if settings.QUERYCOUNTER_ENABLE_PRINT:
            print(self.FIRST + utils.rgb(f'{request.method} {request.get_full_path()}', '#b68'))
        for query in connection.queries[initqueries:]:
            querytime = float(query['time'].strip('[]s'))
            sqltime += querytime
            longest = max(longest, querytime)
            if settings.QUERYCOUNTER_ENABLE_PRINT:
                logstr = self.BULLET + utils.rgb(f'[{querytime:.3f}s] ', '#d93')
                logstr += utils.rgb(query['sql'], '#488')
                print(textwrap.fill(logstr, width=160, subsequent_indent=self.INDENTSTR))
        proctime = runtime - sqltime
        rsummary = f'Request took {runtime:.3f}s ({proctime:.3f}s processing)'
        qsummary = f'{numqueries} queries took {sqltime:.3f}s (longest {longest:.3f}s)'
        if settings.QUERYCOUNTER_ENABLE_PRINT and numqueries:
            print(self.BULLET + utils.rgb(rsummary, '#d93'))
            print(self.LAST + utils.rgb(qsummary, '#d93'))
        if settings.QUERYCOUNTER_ENABLE_HEADERS:
            response['X-Queries'] = qsummary
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
