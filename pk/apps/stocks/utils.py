# encoding: utf-8
from datetime import timedelta


def history_dict(queryset):
    """ Convert a queryset to a dict with date as key. """
    return {h.date:h.close for h in queryset}


def value_for_date(history, dt, ticker):
    """ Given a history dict, return the closest value for the given date. """
    initdtstr = dt.strftime('%Y-%m-%d')
    for i in range(7):
        if dt in history:
            return history[dt]
        dt -= timedelta(days=1)
    raise Exception(f'No value for {ticker} on {initdtstr}')
