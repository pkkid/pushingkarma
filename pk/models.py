#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from collections import defaultdict
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import signals
from django_extensions.db.models import TimeStampedModel
from pk.utils import markdown


class Note(TimeStampedModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    body = models.TextField(help_text='markdown format')
    tags = models.CharField(max_length=255, blank=True, help_text='space delimited')
    authors = models.CharField(max_length=255, default='Michael Shepanski', help_text='comma delimited')
    comments = models.BooleanField(default=True, help_text='allow comments')

    class Meta:
        ordering = ('-created',)
        get_latest_by = 'created'

    def url(self):
        return reverse('note', kwargs={'slug':self.slug})

    def tags(self):
        return sorted(self.tags.split())

    def html(self, anchor=True):
        return [0]

    @classmethod
    def all_tags(cls):
        tags = cache.get('note_tags')
        if tags is None:
            return cls.update_tag_cache()
        return tags

    @classmethod
    def update_tag_cache(cls, **kwargs):
        tags = defaultdict(int)
        for tagstr in Note.objects.values_list('tags', flat=True):
            for tag in filter(bool, tagstr.split(' ')):
                tag = tag.lower().strip()
                tags[tag] += 1
        cache.set('note_tags', dict(tags), None)
        return dict(tags)

signals.post_save.connect(Note.update_tag_cache, sender=Note)
signals.post_delete.connect(Note.update_tag_cache, sender=Note)


class Page(TimeStampedModel):
    slug = models.CharField(max_length=255, unique=True)
    body = models.TextField(help_text='markdown format')
    comments = models.BooleanField(default=True, help_text='allow comments')

    def url(self):
        return reverse('page', kwargs={'slug':self.slug})

    def dict(self):
        html, included = markdown.text_to_html(self.body)
        return {
            'slug': self.slug,
            'body': self.body,
            'html': html,
            'included': included,
        }
