#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from pk.models import Note, Page
from pk.utils import context, markdown as md
from pk.utils import get_object_or_none, response
from pk.utils import response_json_success


def markdown(request):
    text = request.POST.get('text', '')
    html, includes = md.text_to_html(text)
    return response_json_success({'html':html, 'includes':includes})


def notebook(request, template='notebook.html'):
    data = context.core(request, menuitem='notebook')
    if request.method == 'POST':
        note = get_object_or_none(Note, id=request.POST.get('id')) or Note()
        note.title = request.POST.get('title')
        note.body = request.POST.get('text')
        note.tags = request.POST.get('tags')
        if note.body: note.save()
        else: note.delete()
        return response_json_success()
    data.notes = [n.to_dict() for n in Note.objects.all()]
    data.editing = bool(request.COOKIES.get('editing'))
    return response(request, template, data)


def page(request, slug='/', template='page.html'):
    slug = slug or '/'
    page = get_object_or_none(Page, slug=slug) or Page(slug=slug)
    if request.method == 'POST':
        page.body = request.POST.get('text')
        if page.body: page.save()
        else: page.delete()
        return response_json_success()
    data = context.core(request, menuitem='projects')
    data.page = page.dict()
    data.editing = bool(request.COOKIES.get('editing'))
    return response(request, template, data)
