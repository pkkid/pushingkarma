#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from django.views.decorators.csrf import csrf_exempt
from pk.models import Note, Page
from pk.utils import context
from pk.utils import get_object_or_none, response
from pk.utils import response_json_success


def cms(request, slug=None, template='page.html'):
    page = get_object_or_none(Page, slug=slug)
    data = context.core(request, menuitem='projects')
    data.html = page.html() if page else ''
    return response(request, template, data)


def notebook(request, template='notebook.html'):
    data = context.core(request, menuitem='notebook')
    data.tags = sorted(Note.public_tags().items(), key=lambda k,v:v, reverse=True)
    return response(request, template, data)


@csrf_exempt
def markdown(request):
    text = request.POST.get('text', '')
    html = Page.markdown(text)
    return response_json_success({'html':html})
