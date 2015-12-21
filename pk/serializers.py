#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
import re
from django.contrib.auth.models import User
from pk.models import Note, Page
from pk.utils.serializers import DynamicFieldsSerializer
from rest_framework import serializers


class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username','email','date_joined')


class NoteSerializer(DynamicFieldsSerializer):

    class Meta:
        model = Note
        fields = ('id','url','weburl','title','slug','tags','body','html','created','modified')

    def get_tags(self, note):
        return note.tags.split(' ')


class PageSerializer(DynamicFieldsSerializer):

    class Meta:
        model = Page
        fields = ('id','url','weburl','slug','body','html','meta','created','modified')

    def validate_slug(self, value):
        if len(value) <= 0:
            raise serializers.ValidationError('Slug is blank.')
        if not bool(re.match('^[a-z_0-9]{1,64}$', value)):
            raise serializers.ValidationError('Invalid slug, use only a-z, 0-9 and underscore.')
        return value

    def validate_body(self, value):
        if len(value) <= 0:
            raise serializers.ValidationError('Body is blank.')
        return value
