# encoding: utf-8
from collections import defaultdict
from datetime import timedelta
from .models import TickerHistory


def histories_dict(tickers, mindate):
    """ Returns a dict of {ticker: {date: close}} for the given tickers. """
    histories = defaultdict(dict)
    queryset = TickerHistory.objects.filter(ticker__in=tickers, date__gte=mindate)
    queryset = queryset.values_list('ticker_id', 'date', 'close').order_by('-date')
    for item in queryset:
        ticker, date, close = item
        histories[ticker][date] = close
    return histories


def value_for_date(history, dt, ticker):
    """ Given a history dict, return the closest value for the given date. """
    initdtstr = dt.strftime('%Y-%m-%d')
    for _ in range(7):
        if dt in history:
            return history[dt]
        dt -= timedelta(days=1)
    raise Exception(f'No value for {ticker} on {initdtstr}')
