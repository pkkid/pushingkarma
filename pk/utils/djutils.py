# encoding: utf-8
import logging, re, time
from django.db import connection
from pk import utils


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
    

def print_queries(filter=None):
    """ Print all queries executed in this funnction. """
    def wrapper1(func):
        def wrapper2(*args, **kwargs):
            sqltime, longest, numshown = 0.0, 0.0, 0
            initqueries = len(connection.queries)
            starttime = time.time()
            result = func(*args, **kwargs)
            for query in connection.queries[initqueries:]:
                sqltime += float(query['time'].strip('[]s'))
                longest = max(longest, float(query['time'].strip('[]s')))
                if not filter or filter in query['sql']:
                    numshown += 1
                    querystr = utils.rgb('\n[%ss] ' % query['time'], '#d93')
                    querystr += utils.rgb(query['sql'], '#488')
                    print(querystr)
            numqueries = len(connection.queries) - initqueries
            numhidden = numqueries - numshown
            runtime = round(time.time() - starttime, 3)
            proctime = round(runtime - sqltime, 3)
            print(utils.rgb("------", '#488'))
            print(utils.rgb('Total Time:  %ss' % runtime, '#d93'))
            print(utils.rgb('Proc Time:   %ss' % proctime, '#d93'))
            print(utils.rgb('Query Time:  %ss (longest: %ss)' % (sqltime, longest), '#d93'))
            print(utils.rgb('Num Queries: %s (%s hidden)\n' % (numqueries, numhidden), '#d93'))
            return result
        return wrapper2
    return wrapper1


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
