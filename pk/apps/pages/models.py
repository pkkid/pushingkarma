#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
import re
from django.urls import reverse
from django.db import models
from django_extensions.db.models import TimeStampedModel
from pk.utils.markdown import Markdown
from pk.utils.serializers import DynamicFieldsSerializer
from rest_framework import serializers


class Page(TimeStampedModel):
    slug = models.CharField(max_length=255, unique=True)
    body = models.TextField(help_text='markdown format')

    def __str__(self):
        return self.slug

    def weburl(self):
        return reverse('page', kwargs={'slug':self.slug})

    def html(self):
        if getattr(self, '_md', None) is None:
            self._md = Markdown(self.body, Page, '/p/')
        return self._md.html

    def title(self):
        body = self.body.split('\n')
        if len(body) and body[0].startswith('#'):
            return body[0].strip('# ')
        elif len(body) and body[0].startswith('<!--'):
            return body[0].strip('<>!- ')
        return None

    def meta(self):
        if getattr(self, '_md', None) is None:
            self._md = Markdown(self.body, Page, '/p/')
        return self._md.meta


class PageSerializer(DynamicFieldsSerializer):
    class Meta:
        model = Page
        fields = ('id','url','weburl','slug','title','body','html','meta','created','modified')

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
