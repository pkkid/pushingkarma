# encoding: utf-8
import json
from django.conf import settings
from django.core.management import call_command
from django.db import models
from django.dispatch import receiver
from django_extensions.db.models import TimeStampedModel
from pk import log

FUNCTION = 'Weekly Adjusted Time Series'
FUNCTION_KEY = 'TIME_SERIES_WEEKLY_ADJUSTED'
OPEN = '1. open'
HIGH = '2. high'
LOW = '3. low'
CLOSE = '4. close'
ADJCLOSE = '5. adjusted close'
VOLUME = '6. volume'
DIVAMT = '7. dividend amount'


class Stock(TimeStampedModel):
    ticker = models.CharField(max_length=5, unique=True)
    data = models.TextField(help_text='AlphaVantage data')
    description = models.CharField(max_length=255, blank=True, default='')
    tags = models.CharField(max_length=255, blank=True, help_text='space delimited')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __init__(self, *args, **kwargs):
        super(TimeStampedModel, self).__init__(*args, **kwargs)
        self._history = None    # cached decoded json history
        self._keys = None       # cached history keys (dates)

    def __str__(self):
        return self.ticker

    @property
    def history(self):
        if self._history is None:
            data = json.loads(self.data or '{}')
            self._history = data.get(FUNCTION, {})
        return self._history

    @property
    def keys(self):
        if self._keys is None:
            self._keys = sorted(self.history.keys())
        return self._keys

    @property
    def mindate(self):
        dates = self.history.keys()
        return min(dates) if dates else None

    @property
    def maxdate(self):
        dates = self.history.keys()
        return max(dates) if dates else None

    @property
    def close(self):
        return self.value(CLOSE)

    @property
    def adjclose(self):
        return self.value(ADJCLOSE)

    def value(self, key=None, date=None):
        key = key or CLOSE
        date = date or self.maxdate
        return self.history.get(date, {}).get(key)


@receiver(models.signals.post_save, sender=Stock)
def post_save(sender, instance, created, *args, **kwargs):
    if created:
        log.info(f'Calling Django command: updatestocks --ticker={instance.ticker}')
        call_command('updatestocks', ticker=instance.ticker)
