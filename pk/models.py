#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from django.core.urlresolvers import reverse
from django.db import models
from django_extensions.db.models import TimeStampedModel
from pk.utils import markdown


class Note(TimeStampedModel):
    title = models.CharField(max_length=255)
    body = models.TextField(help_text='markdown format')
    tags = models.CharField(max_length=255, blank=True, help_text='space delimited')

    def url(self):
        return reverse('note', kwargs={'slug':self.slug})

    def dict(self):
        html, includes = markdown.text_to_html(self.body)
        return dict(
            id = self.id,
            title = self.title,
            body = self.body,
            html = html,
            tags = self.tags.split(' '),
            includes = includes,
        )


class Page(TimeStampedModel):
    slug = models.CharField(max_length=255, unique=True)
    body = models.TextField(help_text='markdown format')

    def url(self):
        return reverse('page', kwargs={'slug':self.slug})

    def dict(self):
        html, includes = markdown.text_to_html(self.body)
        return dict(
            id = self.id,
            slug = self.slug,
            body = self.body,
            html = html,
            includes = includes,
        )