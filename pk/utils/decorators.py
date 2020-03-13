# encoding: utf-8
import functools, json, os, time
from django.core.cache import cache
from django.db import connection
from django.http import HttpResponse
from rest_framework.response import Response
from pk import log

COLORS = {'blue':34, 'cyan':36, 'green':32, 'grey':30, 'magenta':35, 'red':31, 'white':37, 'yellow':33}
RESET = '\033[0m'


class ContextDecorator(object):
    def __call__(self, f):
        @functools.wraps(f)
        def decorated(*args, **kwds):
            with self:
                return f(*args, **kwds)
        return decorated


def _response_to_data(response):
    """ Convert a response object to data dict. """
    if response.__class__.__name__ == 'HttpResponse':
        return {'type':'HttpResponse', 'kwargs':{
            'content': str(response.content),
            'content_type': response['Content-Type'],
        }}
    elif response.__class__.__name__ == 'Response':
        return {'type':'Response', 'kwargs':{
            'data': response.data,
        }}


def _get_response(cachekey):
    """ Convert a data dict to a response object. """
    try:
        data = json.loads(cache.get(cachekey, '{}'))
        if data.get('type') == 'Response':
            return Response(**data['kwargs'])
        elif data.get('type') == 'HttpResponse':
            return HttpResponse(**data['kwargs'])
    except Exception as err:
        log.warning(f'Unable to read cached content for {cachekey}; {err}')
    return None


def cache_api_data(timeout, key=None):
    def wrapper1(func):
        def wrapper2(request, *args, **kwargs):
            cachekey = key or f'{func.__module__}.{func.__name__}'
            force = request.GET.get('force') == '1'
            response = _get_response(cachekey)
            if not response or force:
                response = func(request, *args, **kwargs)
                data = _response_to_data(response)
                cache.set(cachekey, json.dumps(data), timeout)
            return response
        return wrapper2
    return wrapper1


def color(text, color=None):
    """ Colorize text {red, green, yellow, blue, magenta, cyan, white}. """
    if os.getenv('ANSI_COLORS_DISABLED') is None:
        fmt_str = '\033[%dm%s'
        if color is not None:
            text = fmt_str % (COLORS[color], text)
        text += RESET
    return text


def lazyproperty(func):
    """ Decorator that makes a property lazy-evaluated.
        http://stevenloria.com/lazy-evaluated-properties-in-python/
    """
    attr_name = '_lazy_%s' % func.__name__
    @property  # noqa
    def wrapper(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, func(self))
        return getattr(self, attr_name)
    return wrapper


def log_exception():
    def wrapper1(func):
        def wrapper2(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as err:
                log.exception(err)
        return wrapper2
    return wrapper1


class log_queries(ContextDecorator):
    def __init__(self, label=None, filter=None, show_queries=True):
        self.label = label
        self.filter = filter
        self.show_queries = show_queries

    def __enter__(self):
        if self.label:
            log.info(color('-' * 25, 'blue'))
            log.info(color('%s - start of profiling' % self.label, 'blue'))
            log.info(color('-' * 25, 'blue'))
        self.sqltime, self.longest, self.numshown = 0.0, 0.0, 0
        self.initqueries = len(connection.queries)
        self.starttime = time.time()
        return self

    def __exit__(self, *exc):
        for query in connection.queries[self.initqueries:]:
            self.sqltime += float(query['time'].strip('[]s'))
            self.longest = max(self.longest, float(query['time'].strip('[]s')))
            if self.show_queries:
                if not self.filter or self.filter in query['sql']:
                    self.numshown += 1
                    querystr = color('[%ss] ' % query['time'], 'yellow')
                    querystr += color(query['sql'], 'blue')
                    log.info('')
                    log.info(querystr)
        numqueries = len(connection.queries) - self.initqueries
        numhidden = numqueries - self.numshown
        runtime = round(time.time() - self.starttime, 3)
        proctime = round(runtime - self.sqltime, 3)
        log.info(color('-' * 8, 'blue'))
        if self.label:
            log.info(color('%s - end of profiling' % self.label, 'blue'))
            log.info(color('-' * 8, 'blue'))
        log.info(color('Total Time:  %ss' % runtime, 'yellow'))
        log.info(color('Proc Time:   %ss' % proctime, 'yellow'))
        log.info(color('Query Time:  %ss (longest: %ss)' % (self.sqltime, self.longest), 'yellow'))
        log.info(color('Num Queries: %s (%s hidden)\n' % (numqueries, numhidden), 'yellow'))
