# encoding: utf-8
from django.views.decorators.csrf import ensure_csrf_cookie
from pk import utils


@ensure_csrf_cookie
def index(request, tmpl='index.html'):
    return utils.response(request, tmpl, {})
