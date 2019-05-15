#!/usr/bin/env python
# encoding: utf-8
import hashlib, json, queue
from threading import Thread
from django.conf import settings
from django.forms.utils import ErrorDict
from django.http import HttpResponse
from django.shortcuts import render


def get_object_or_none(cls, *args, **kwargs):
    try:
        return cls._default_manager.get(*args, **kwargs)  # noqa; pylint:disable=protected-access
    except cls.DoesNotExist:
        return None


def hash_args(*args, **kwargs):
    hashobj = hashlib.md5()
    for arg in sorted(args):
        hashobj.update(str(arg).encode())
    for key, value in sorted(kwargs.items()):
        hashobj.update(str(key).encode())
        hashobj.update(str(value).encode())
    return hashobj.hexdigest()[:7]


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


def response_json_error(errors, data=None):
    data = data or {}
    data['success'] = False
    data['errors'] = errors if isinstance(errors, (dict, ErrorDict)) else {'__all__': errors}
    return response_json(data)


def response_json_success(data=None):
    data = data or {}
    data['success'] = True
    return response_json(data)


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


def update(obj, **kwargs):
    for key, val in kwargs.items():
        setattr(obj, key, val)
    obj.save()
