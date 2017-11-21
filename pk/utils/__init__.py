#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
import json
from django.conf import settings
from django.forms.utils import ErrorDict
from django.http import HttpResponse
from django.shortcuts import render
from django.template import RequestContext
from django.template.loader import render_to_string


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


def response_json_error(errors, data=None):
    data = data or {}
    data['success'] = False
    data['errors'] = errors if type(errors) in [dict, ErrorDict] else {'__all__': errors}
    return response_json(data)


def response_json_success(data=None):
    data = data or {}
    data['success'] = True
    return response_json(data)


def response_modal(request, template, data):
    modal = render_to_string(template, data, context_instance=RequestContext(request))
    return response_json_success(dict(modal=modal))


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
    except:
        return default


def rset(obj, attrstr, value, delim='.'):
    parts = attrstr.split(delim, 1)
    attr = parts[0]
    attrstr = parts[1] if len(parts) == 2 else None
    if attr not in obj: obj[attr] = {}
    if attrstr: rset(obj[attr], attrstr, value, delim)
    else: obj[attr] = value


def update(obj, **kwargs):
    for key,val in kwargs.items():
        setattr(obj, key, val)
    obj.save()
