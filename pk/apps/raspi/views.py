#!/usr/bin/env python
# encoding: utf-8
import requests
from django.conf import settings
from pk import log, utils
from pk.apps.calendar.views import get_events
from pk.utils import context
from pk.utils.decorators import cached


def raspi(request, tmpl='raspi.html'):
    data = context.core(request)
    data.weather = _get_weather()
    data.calendar = _get_calendar()
    data.news = _get_news()
    # import pprint; pprint.pprint(data.weather)
    return utils.response(request, tmpl, data)


@cached(timeout=900, key='raspi-weather')
def _get_weather():
    try:
        response = requests.get(settings.RASPI_WU_URL)
        return response.json()
    except Exception as err:
        log.exception(err)


@cached(key='raspi-calendar')
def _get_calendar():
    try:
        response = get_events(settings.RASPI_CALENDAR_URL)
        return response
    except Exception as err:
        log.exception(err)


@cached(key='raspi-news')
def _get_news():
    return None
