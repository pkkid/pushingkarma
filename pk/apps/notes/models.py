# encoding: utf-8
from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify
from django_extensions.db.models import TimeStampedModel

PRIVATE = 'private'


class Note(TimeStampedModel):
    slug = models.SlugField(max_length=255, unique=True, default=None)
    title = models.CharField(max_length=255, blank=True)
    body = models.TextField(help_text='markdown format')
    tags = models.CharField(max_length=255, blank=True, help_text='space delimited')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.slug

    def is_private(self):
        return PRIVATE in self.list_tags()

    def list_tags(self):
        return self.tags.lower().split(' ')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Note, self).save(*args, **kwargs)

    def weburl(self):
        return f'{settings.DOMAIN}/notes?id={self.id}'
