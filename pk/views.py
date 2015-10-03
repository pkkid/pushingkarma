#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from pk.models import Note, Page
from pk.utils import context
from pk.utils import get_object_or_none, response
from pk.utils import response_json_success


def page(request, slug='/', template='page.html'):
    slug = slug or '/'
    page = get_object_or_none(Page, slug=slug) or Page(slug=slug)
    if request.method == 'POST':
        page.body = request.POST.get('text')
        page.save()
        return response_json_success()
    data = context.core(request, menuitem='projects')
    data.page = page.dict()
    return response(request, template, data)


def markdown(request):
    text = request.POST.get('text', '')
    html = Page.markdown(text)
    return response_json_success({'html':html})


def notebook(request, template='notebook.html'):
    data = context.core(request, menuitem='notebook')
    data.tags = sorted(Note.public_tags().items(), key=lambda k,v:v, reverse=True)
    return response(request, template, data)
