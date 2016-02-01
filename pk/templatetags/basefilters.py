"""
General useful filters.
"""
import json as _json
from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe
register = template.Library()


@register.filter
def browser(request):
    agent = request.META['HTTP_USER_AGENT'].lower()
    browsers = ('chrome', 'firefox', 'msie', 'safari')
    for browser in browsers:
        if browser in agent:
            return browser
    return ''


@register.filter
def dict_value(arg, key, default=''):
    if isinstance(arg, dict):
        return arg.get(key, default)
    return default


@register.filter
def html_encode(arg):
    return escape(arg)


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
