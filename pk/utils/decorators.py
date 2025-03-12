# encoding: utf-8
import json, logging
from django.core.cache import cache
from django.http import HttpResponse
from rest_framework.response import Response
log = logging.getLogger(__name__)


def _response_to_data(response):
    """ Convert a response object to data dict. """
    if response.__class__.__name__ == 'HttpResponse':
        return {'type':'HttpResponse', 'kwargs':{
            'content': str(response.content),
            'content_type': response['Content-Type'],
        }}
    elif response.__class__.__name__ == 'Response':
        return {'type':'Response', 'kwargs':{'data': response.data}}


def _get_response(cachekey):
    """ Convert a data dict to a response object. """
    try:
        data = json.loads(cache.get(cachekey, '{}'))
        if data.get('type') == 'Response': return Response(**data['kwargs'])
        elif data.get('type') == 'HttpResponse': return HttpResponse(**data['kwargs'])
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


def log_exception(logger=None):
    logger = logger or log
    def wrapper1(func):  # noqa
        def wrapper2(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as err:
                logger.exception(err)
        return wrapper2
    return wrapper1
