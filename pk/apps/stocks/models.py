# encoding: utf-8
import json
from django.conf import settings
from django.core.management import call_command
from django.db import models
from django.dispatch import receiver
from django_extensions.db.models import TimeStampedModel
from pk import log

PROVIDERS = {
    'alphavantage': {
        'url': 'https://www.alphavantage.co/query?symbol={ticker}&function=TIME_SERIES_WEEKLY_ADJUSTED&apikey={apikey}',
        'apikey': settings.ALPHAVANTAGE_APIKEY,
        'limit': 60,  # per minute (limit 25/day!)
        'limitstr': 'API rate limit',
        'historykey': 'Weekly Adjusted Time Series',
        'closekey': '4. close',
        'adjclosekey': '5. adjusted close',
    },
    'finazon': {
        'url': 'https://api.finazon.io/latest/time_series?dataset=us_stocks_essential&ticker={ticker}&interval=1d&apikey={apikey}',
        'apikey': settings.FINAZON_APIKEY,
        'limit': 30,  # per minute
        'limitstr': 'API_RATE_LIMIT_EXCEEDED',
        'historykey': 'data',
        'close': 'c',
        'adjclose': 'a',
    }
}
PROVIDER = PROVIDERS['finazon']


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
            self._history = data.get(PROVIDER.get('historykey'), {})
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
        return self.value(PROVIDER.get('closekey'))

    @property
    def adjclose(self):
        return self.value(PROVIDER.get('adjclosekey'))

    def value(self, key=None, date=None):
        key = key or PROVIDER.get('closekey')
        date = date or self.maxdate
        return self.history.get(date, {}).get(key)


@receiver(models.signals.post_save, sender=Stock)
def post_save(sender, instance, created, *args, **kwargs):
    if created:
        log.info(f'Calling Django command: updatestocks --ticker={instance.ticker}')
        call_command('updatestocks', ticker=instance.ticker)
