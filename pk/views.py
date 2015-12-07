#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from pk.models import Note, Page
from pk.utils import context, markdown as md
from pk.utils import get_object_or_none, response
from pk.utils import response_json_success


def note(request, slug=None, template='note.html'):
    data = context.core(request, menuitem='notebook')
    data.note = get_object_or_none(Note, slug=slug) or Note()
    data.editing = bool(request.COOKIES.get('editing'))
    return response(request, template, data)

    # noteid = request.POST.get('id') or None
    # note = get_object_or_none(Note, id=noteid) if noteid else None
    # note = get_object_or_none(Note, slug=slug) if not note and slug else None
    # note = note or Note()
    # if request.method == 'POST':
    #     note.title = request.POST.get('title')
    #     note.body = request.POST.get('text')
    #     note.tags = request.POST.get('tags')
    #     if note.body:
    #         note.save()
    #         return response_json_success(note.dict())
    #     else:
    #         note.delete()
    #         return response_json_success()
    # data.note = note.dict()
    # data.notes = [n.dict() for n in Note.objects.all()]
    # data.editing = bool(request.COOKIES.get('editing'))
    # return response(request, template, data)


def page(request, slug='root', template='page.html'):
    data = context.core(request, menuitem='projects')
    data.page = get_object_or_none(Page, slug=slug) or Page(slug=slug)
    data.editing = bool(request.COOKIES.get('editing'))
    return response(request, template, data)


def markdown(request):
    text = request.POST.get('text', '')
    title = request.POST.get('title')
    html, includes = md.text_to_html(text)
    if title:
        html = '<h3>%s</h3>\n%s' % (title, html)
    return response_json_success({'html': html, 'includes': includes})
