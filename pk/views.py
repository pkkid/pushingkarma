#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from django.http import HttpResponse
from pk.models import Note, Page
from pk.serializers import NoteSerializer, PageSerializer
from pk.utils import get_object_or_none, context, response, response_json
from pk.utils.markdown import Markdown


def note(request, slug=None, template='note.html'):
    note = get_object_or_none(Note, slug=slug) or Note.objects.order_by('-modified')[0]
    data = context.core(request, menuitem='notebook')
    data.note = NoteSerializer(note, context={'request':request}).data
    return response(request, template, data)


def page(request, slug='root', template='page.html'):
    page = get_object_or_none(Page, slug=slug) or Page(slug=slug)
    data = context.core(request, menuitem='projects')
    data.page = PageSerializer(page, context={'request':request}).data
    return response(request, template, data)


def markdown(request, prefix):
    body = request.POST.get('body', '')
    if prefix == '/n/':
        md = Markdown(body)
        html = '<h2>%s</h2>%s' % (request.POST.get('title',''), md.html)
        return response_json({'html':html})
    elif prefix == '/p/':
        md = Markdown(body, Page, prefix)
        includes = sorted(md.meta['includes'].keys())
        return response_json({'html':md.html, 'includes':includes})
    return HttpResponse(status=400)
