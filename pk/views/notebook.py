#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from pushingkarma.apps.notebook.models import Note
from pushingkarma.utils import context, response


def overview(request, template='notebook/overview.html'):
    data = context.core(request, menuitem='notebook')
    data.tags = sorted(Note.public_tags().items(), key=lambda k,v:v, reverse=True)
    return response(request, template, data)


# def note(request, slug, template='notebook/blogpost.html'):
#     data = context.core(menuitem='notebook')
#     data.note = get_object_or_404(Note, slug=slug)
#     return response(request, template, data)
