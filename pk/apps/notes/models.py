#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify
from django_extensions.db.models import TimeStampedModel
from pk.utils.markdown import Markdown
from pk.utils.serializers import DynamicFieldsSerializer


class Note(TimeStampedModel):
    slug = models.SlugField(max_length=255, unique=True, default=None)
    title = models.CharField(max_length=255)
    body = models.TextField(help_text='markdown format')
    tags = models.CharField(max_length=255, blank=True, help_text='space delimited')

    def __str__(self):
        return self.slug

    def weburl(self):
        return reverse('note', kwargs={'slug':self.slug})

    def html(self):
        if getattr(self, '_md', None) is None:
            self._md = Markdown(self.body)
        return self._md.html

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Note, self).save(*args, **kwargs)


class NoteSerializer(DynamicFieldsSerializer):
    class Meta:
        model = Note
        fields = ('id','url','weburl','title','slug','tags','body','html','created','modified')

    def get_tags(self, note):
        return note.tags.split(' ')
