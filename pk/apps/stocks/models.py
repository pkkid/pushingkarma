#!/usr/bin/env python
# encoding: utf-8
import json
from django.db import models
from django_extensions.db.models import TimeStampedModel
from pk.utils.serializers import DynamicFieldsSerializer

FUNCTION = 'Weekly Adjusted Time Series'
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

    def __init__(self, *args, **kwargs):
        super(TimeStampedModel, self).__init__(*args, **kwargs)
        self._history = None

    def __str__(self):
        return self.ticker

    @property
    def history(self):
        if self._history is None:
            data = json.loads(self.data or '{}')
            self._history = data.get(FUNCTION, {})
        return self._history

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


class StockSerializer(DynamicFieldsSerializer):
    class Meta:
        model = Stock
        fields = ('id','url','ticker','description','close',
            'mindate','maxdate','modified','tags','history')
