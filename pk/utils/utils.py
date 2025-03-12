# encoding: utf-8
import json, queue, requests
from decimal import Decimal
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from threading import Thread


def clean_amount(value):
    """ Clean a USD string such as -$99.99 to a Decimal value. """
    if isinstance(value, str):
        value = value.replace('$', '')
        value = value.replace(',', '')
        return Decimal(value)
    if isinstance(value, (int, float)):
        return Decimal(value)
    return value


def get_object_or_none(cls, *args, **kwargs):
    try:
        return cls._default_manager.get(*args, **kwargs)
    except cls.DoesNotExist:
        return None


def move_to_end(odict, *keys):
    for key in keys:
        if key in odict:
            odict.move_to_end(key)
    return odict


def response(request, template, data):
    if 'json' in request.GET:
        return response_json(data)
    data['settings'] = settings
    return render(request, template, data)


def response_json(data, status=200):
    json.encoder.FLOAT_REPR = lambda f: ('%.5f' % f)  # fix floats
    data = json.dumps(dict(data), default=lambda x: str(x), sort_keys=True)
    return HttpResponse(data, content_type='application/json', status=status)


def rget(obj, attrstr, default=None, delim='.'):
    try:
        parts = attrstr.split(delim, 1)
        attr = parts[0]
        attrstr = parts[1] if len(parts) == 2 else None
        if isinstance(obj, dict): value = obj[attr]
        elif isinstance(obj, list): value = obj[int(attr)]
        elif isinstance(obj, tuple): value = obj[int(attr)]
        elif isinstance(obj, object): value = getattr(obj, attr)
        if attrstr: return rget(value, attrstr, default, delim)
        return value
    except Exception:
        return default


def rset(obj, attrstr, value, delim='.'):
    parts = attrstr.split(delim, 1)
    attr = parts[0]
    attrstr = parts[1] if len(parts) == 2 else None
    if attr not in obj: obj[attr] = {}
    if attrstr: rset(obj[attr], attrstr, value, delim)
    else: obj[attr] = value


def threaded(numthreads=10, **kwargs):
    """ Call all resultkey -> (callback, [*args]) pairs in parallel.
        Results are returned as a dictionary with kwarg key as the keys.
    """
    jobs = queue.Queue()
    threads, results = [], {}
    numthreads = min(numthreads, len(kwargs))
    for key, meta in kwargs.items():
        results[key] = None
        jobs.put([key] + meta)
    for _ in range(numthreads):
        threads.append(Thread(target=_threadwrap, args=[jobs, results]))
        threads[-1].setDaemon(True)
        threads[-1].start()
    for thread in threads:
        thread.join()
    return results


def _threadwrap(jobs, results):
    try:
        while True:
            key, callback, *args = jobs.get_nowait()
            results[key] = callback(*args)
    except queue.Empty:
        pass


def toback(obj, *keys):
    """ Move keys to the back of dict. """
    for key in keys:
        value = obj.pop(key)
        obj[key] = value
    return obj


def vue_devserver_running(request):
    """ Return url if it looks like the Vue devserver is running. """
    try:
        if not settings.DEBUG:
            return None
        servername = rget(request, 'environ.SERVER_NAME', 'localhost')
        serverurl = f'http://{servername}:5173'
        requests.head(serverurl)
        return serverurl
    except Exception:
        return None
