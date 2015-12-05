#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify
from django_extensions.db.models import TimeStampedModel
from pk.utils import markdown


class Note(TimeStampedModel):
    slug = models.SlugField(editable=False, primary_key=True)
    title = models.CharField(max_length=255)
    body = models.TextField(help_text='markdown format')
    tags = models.CharField(max_length=255, blank=True, help_text='space delimited')

    def __str__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.slug)

    def apiurl(self):
        return reverse('notes-detail')

    def weburl(self):
        return reverse('note', kwargs={'slug':self.slug})

    def html(self):
        if getattr(self, '_html', None) is None:
            self._html, self._includes = markdown.text_to_html(self.body)
        return self._html

    def includes(self):
        if getattr(self, '_includes', None) is None:
            self.html()
        return self._includes

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Note, self).save(*args, **kwargs)


class Page(TimeStampedModel):
    slug = models.CharField(max_length=255, primary_key=True)
    body = models.TextField(help_text='markdown format')

    def __str__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.slug)

    def apiurl(self):
        return reverse('pages-detail')

    def weburl(self):
        return reverse('page', kwargs={'slug':self.slug})

    def html(self):
        if getattr(self, '_html', None) is None:
            self._html, self._includes = markdown.text_to_html(self.body)
        return self._html

    def includes(self):
        if getattr(self, '_includes', None) is None:
            self.html()
        return self._includes
