#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
import markdown
from collections import defaultdict
from datetime import datetime
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import signals
from django_extensions.db.models import TimeStampedModel

STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('public', 'Public'),
    ('private', 'Private')
]


class Note(TimeStampedModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    body = models.TextField()
    tags = models.CharField(max_length=255, blank=True, help_text='space delimited')
    authors = models.CharField(max_length=255, default='Michael Shepanski', help_text='comma delimited')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='public')
    allow_comments = models.BooleanField(default=True)
    published = models.DateTimeField(default=datetime.now)

    class Meta:
        ordering = ('-published',)
        get_latest_by = 'published'

    def url(self):
        return reverse('notebook_note', kwargs={'slug': self.slug})

    def tags(self):
        return sorted(self.tags.split())

    def html(self, anchor=True):
        return markdown.markdown(self.body, safe_mode=False)

    @classmethod
    def public_notes(cls):
        notes = cls.objects.filter(status='public')
        notes = notes.filter(published__lte=datetime.now())
        return notes

    @classmethod
    def public_tags(cls):
        public_tags = cache.get('notebook_public_tags')
        if public_tags is None:
            return update_tags_cache()
        return public_tags


def update_tags_cache(sender=None, instance=None, created=None, **kwargs):
    public_tags = defaultdict(int)
    for post in Note.public_notes():
        for tag in filter(bool, post.tags.split(' ')):
            tag = tag.lower().strip()
            public_tags[tag] += 1 if tag else 0
    public_tags = dict(public_tags)
    cache.set('notebook_public_tags', public_tags, 999999999)
    return public_tags


signals.post_save.connect(update_tags_cache, sender=Note)
signals.post_delete.connect(update_tags_cache, sender=Note)
