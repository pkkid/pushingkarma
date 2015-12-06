#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from rest_framework import viewsets
from rest_framework.response import Response
from pk.models import Note, Page
from pk import serializers
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class NotesViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.order_by('-created')
    serializer_class = serializers.NoteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    list_fields = ['url', 'title', 'tags', 'created', 'modified']

    def list(self, request, *args, **kwargs):
        notes = Note.objects.order_by('-created')
        serializer = serializers.NoteSerializer(notes, context={'request':request},
            many=True, fields=self.list_fields)
        return Response(serializer.data)


class PagesViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.order_by('-created')
    serializer_class = serializers.PageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    list_fields = ['url', 'slug', 'created', 'modified']

    def list(self, request, *args, **kwargs):
        queryset = Page.objects.order_by('-created')
        serializer = serializers.PageSerializer(queryset, context={'request':request},
            many=True, fields=self.list_fields)
        return Response(serializer.data)
