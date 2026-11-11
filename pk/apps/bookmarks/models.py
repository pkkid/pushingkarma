# encoding: utf-8
from django.conf import settings
from django.db import models
from pk.utils.django import TimeStampedModel

LINK, FOLDER, SEPARATOR = 'link', 'folder', 'separator'
KINDS = ((LINK, 'Link'), (FOLDER, 'Folder'), (SEPARATOR, 'Separator'))


class Bookmark(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)
    kind = models.CharField(max_length=10, choices=KINDS, default=LINK)
    title = models.CharField(max_length=255, blank=True, default='')
    url = models.TextField(blank=True, default='')
    sortid = models.IntegerField(default=0)

    class Meta:
        ordering = ('sortid', 'id')

    def __str__(self):
        return f'<Bookmark:{self.id}:{self.kind}:{self.title}>'
