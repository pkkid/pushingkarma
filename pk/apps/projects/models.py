# encoding: utf-8
import logging
from django.db import models
from pk.utils.django import TimeStampedModel
log = logging.getLogger(__name__)


class GithubRepo(TimeStampedModel):
    """ Stats and commit history for a GitHub repository. Refreshed hourly by the
        update_projects management command. The modified field doubles as the time
        of the last successful sync. The icon and color are set by hand and are never
        touched by the sync, so they can be changed in one place for the whole site.
    """
    name = models.CharField(max_length=255, primary_key=True)  # owner/repo
    description = models.TextField(null=True, blank=True)
    homepage = models.CharField(max_length=255, null=True, blank=True)
    language = models.CharField(max_length=64, null=True, blank=True)
    license = models.CharField(max_length=64, null=True, blank=True)
    stars = models.IntegerField(default=0)
    forks = models.IntegerField(default=0)
    issues = models.IntegerField(default=0)
    pushed = models.DateTimeField(null=True, blank=True)
    commits = models.JSONField(default=dict, help_text='Commit counts per day {YYYY-MM-DD: count}')
    icon = models.TextField(null=True, blank=True, help_text='mdi icon class or raw <svg> markup')
    color = models.CharField(max_length=32, null=True, blank=True, help_text='CSS color for the icon')

    def __str__(self):
        return f'<GithubRepo:{self.name}>'
