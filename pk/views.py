#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from pk.models import Note, Page
from pk.utils import get_object_or_none, context, response, response_json
from pk.utils.markdown import Markdown


def note(request, slug=None, template='note.html'):
    data = context.core(request, menuitem='notebook')
    data.note = get_object_or_none(Note, slug=slug) or Note()
    data.editing = bool(request.COOKIES.get('editing'))
    return response(request, template, data)


def page(request, slug='root', template='page.html'):
    data = context.core(request, menuitem='projects')
    data.page = get_object_or_none(Page, slug=slug) or Page(slug=slug)
    data.editing = bool(request.COOKIES.get('editing'))  # TODO Remove?
    return response(request, template, data)


def markdown(request):
    body = request.POST.get('body', '')
    mtype = request.POST.get('type')
    if mtype == 'pages':
        md = Markdown(body, Page, '/p/')
        return response_json({'html':md.html, 'includes':md.meta['includes'].keys()})
    elif mtype == 'notes':
        md = Markdown(body)
        return response_json({'html':md.html})
    return response_json({'message':'Unknown type'}, status=400)
