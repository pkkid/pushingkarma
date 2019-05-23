# encoding: utf-8
import os
import json as _json
from django import template
from django.conf import settings
from django.utils.html import escape
from django.utils.safestring import mark_safe
register = template.Library()


@register.filter
def browser(request):
    agent = request.META['HTTP_USER_AGENT'].lower()
    browsers = ('chrome', 'firefox', 'msie', 'safari')
    for name in browsers:
        if name in agent:
            return name
    return ''


@register.filter
def dict_value(arg, key, default=''):
    if isinstance(arg, dict):
        return arg.get(key, default)
    return default


@register.filter
def html_encode(arg):
    return escape(arg)


@register.simple_tag()
def include_verbatim(path):
    for template_conf in settings.TEMPLATES:
        for template_dir in template_conf.get('DIRS', []):
            filepath = '%s/%s' % (template_dir, path)
            if os.path.isfile(filepath):
                with open(filepath, 'r') as fp:
                    return mark_safe(fp.read())


@register.filter
def join_by(arg, delim=', '):
    return delim.join(arg)


@register.filter
def json(arg):
    if not arg: return 'null'
    return mark_safe(_json.dumps(arg))


@register.filter
def is_false(arg):
    return arg is False


@register.filter
def is_true(arg):
    return arg is True


@register.filter
def sort(sortable):
    return sorted(sortable)


@register.filter
def to_bool(arg, default='false'):
    if isinstance(arg, bool): return arg
    if isinstance(arg, str) and arg.lower() == 'true': return True
    return True if default.lower() == 'true' else False


@register.filter
def to_int(value):
    try:
        return int(float(value))
    except Exception:
        return '--'
