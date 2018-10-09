#!/usr/bin/env python
# encoding: utf-8
import requests
from django.conf import settings
from pk import log, utils
from pk.apps.calendar.views import get_events
from pk.utils import auth, context
from pk.utils.decorators import softcache


def raspi(request, tmpl='raspi.html'):
    data = context.core(request)
    data.weather = _get_weather(request)
    data.calendar = _get_calendar(request)
    data.news = _get_news(request)
    data.tasks = _get_tasks(request)
    return utils.response(request, tmpl, data)


@softcache(timeout=900, key='raspi-weather')
def _get_weather(request):
    try:
        response = requests.get(settings.RASPI_WU_URL)
        return response.json()
    except Exception as err:
        log.exception(err)


@softcache(key='raspi-calendar')
def _get_calendar(request):
    try:
        response = get_events(settings.RASPI_CALENDAR_URL)
        return response
    except Exception as err:
        log.exception(err)


@softcache(key='raspi-tasks')
def _get_tasks(request):
    try:
        service = auth.get_gauth_service(settings.EMAIL, 'tasks')
        tasklists = service.tasklists().list().execute()
        tasklists = {tlist['title']:tlist for tlist in tasklists['items']}
        tasklist = tasklists['My Tasks']
        tasks = service.tasks().list(tasklist=tasklist['id']).execute()
        tasks = sorted(tasks['items'], key=lambda x:x['position'])
        return tasks
    except Exception as err:
        log.exception(err)


@softcache(key='raspi-news')
def _get_news(request):
    return None
