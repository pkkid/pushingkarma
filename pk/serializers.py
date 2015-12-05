#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from pk.models import Note, Page
from pk.utils.serializers import DynamicFieldsSerializer


class NoteSerializer(DynamicFieldsSerializer):

    class Meta:
        model = Note
        fields = ('url', 'title', 'slug', 'tags', 'body', 'html', 'includes', 'created', 'modified')

    def get_url(self, note):
        return note.apiurl()

    def get_tags(self, note):
        return note.tags.split(',')


class PageSerializer(DynamicFieldsSerializer):

    class Meta:
        model = Page
        fields = ('url', 'slug', 'body', 'html', 'includes', 'created', 'modified')

    def get_url(self, note):
        return note.apiurl()
