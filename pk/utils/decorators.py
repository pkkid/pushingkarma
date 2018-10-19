#!/usr/bin/env python
# encoding: utf-8
import functools, json, os, time
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.http import Http404
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


def softcache(timeout=900, expires=86400, key=None, force=False):
    def wrapper1(func):
        def wrapper2(*args, **kwargs):
            now = int(time.time())
            value = json.loads(cache.get(key, '{}'))
            age = now - value.get('lastupdate', 0)
            if value and age <= timeout and value.get('data') and not force:
                log.info('Returning cached value for: %s', key)
                return value['data']
            try:
                log.info('Fetching new value for: %s', key)
                result = func(*args, **kwargs)
                cache.set(key, json.dumps({'lastupdate':now,
                    'data':result}), expires)
                return result
            except Exception as err:
                log.warning('Error fetching new value: %s', err)
                return value['data']
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


def login_or_apikey_required(func):
    apikey = getattr(settings, 'APIKEY', None)
    def wrapper(request, *args, **kwargs):  # noqa
        if request.user.is_authenticated or (apikey and request.GET.get('apikey') == apikey):
            return func(request, *args, **kwargs)
        from django.shortcuts import redirect
        return redirect(settings.LOGIN_URL)
    return wrapper


class logqueries(ContextDecorator):
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
