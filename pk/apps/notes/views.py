#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from pk import utils
from pk.utils.markdown import Markdown
from pk.utils.search import FIELDTYPES, SearchField, Search
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .models import Note, NoteSerializer

NOTESEARCHFIELDS = {
    'title': SearchField(FIELDTYPES.STR, 'title'),
    'body': SearchField(FIELDTYPES.STR, 'body'),
    'tags': SearchField(FIELDTYPES.STR, 'tags'),
}


def note(request, slug=None, tmpl='note.html'):
    note = utils.get_object_or_none(Note, slug=slug)
    if note is None:
        search = request.GET.get('search')
        notes = Note.objects.order_by('-modified')
        notes = Search(notes, NOTESEARCHFIELDS, search).queryset() if search else notes
        note = notes[0] if notes.exists() else None
    data = utils.context.core(request, menuitem='notes')
    data.note = NoteSerializer(note, context={'request':request}).data
    return utils.response(request, tmpl, data)


def markdown(request):
    body = request.POST.get('body', '')
    md = Markdown(body)
    html = md.html
    if request.POST.get('title',''):
        html = '<h2>%s</h2>%s' % (request.POST['title'], html)
    return utils.response_json({'html':html})


class NotesViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.order_by('-modified')
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    list_fields = ['id','url','weburl','title','tags','created','modified']

    def list(self, request, *args, **kwargs):
        searchdata = {}
        searchstr = request.GET.get('search')
        notes = Note.objects.order_by('-modified')
        if searchstr:
            search = Search(notes, NOTESEARCHFIELDS, searchstr)
            notes = search.queryset()
            searchdata = {'searchstr':searchstr, 'errors':search.errors, 'datefilters': search.datefilters}
        page = self.paginate_queryset(notes)
        serializer = NoteSerializer(page, context={'request':request}, many=True, fields=self.list_fields)
        response = self.get_paginated_response(serializer.data)
        response.data.update(searchdata)
        response.data.move_to_end('results')
        return response
