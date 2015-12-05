#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from pk.models import Note, Page
from pk import serializers


class NotesViewSet(viewsets.ViewSet):
    queryset = Note.objects.order_by('-created')

    def list(self, request):
        queryset = Note.objects.order_by('-created')
        serializer = serializers.NoteSerializer(queryset, context={'request':request},
            many=True, fields=['url', 'title', 'tags'])
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Note.objects.all()
        note = get_object_or_404(queryset, pk=pk)
        serializer = serializers.NoteSerializer(note, context={'request':request})
        return Response(serializer.data)


class PagesViewSet(viewsets.ViewSet):
    queryset = Page.objects.order_by('-created')

    def list(self, request):
        queryset = Page.objects.order_by('-created')
        serializer = serializers.PageSerializer(queryset, context={'request':request},
            many=True, fields=['url', 'slug'])
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Page.objects.all()
        page = get_object_or_404(queryset, pk=pk)
        serializer = serializers.PageSerializer(page, context={'request':request})
        return Response(serializer.data)
