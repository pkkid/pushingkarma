#!/usr/bin/env python
# encoding: utf-8
import pprint, requests
from django.conf import settings
from django.core.management.base import BaseCommand
from pk.apps.calendar.views import get_events
from pk.utils.decorators import cached
from pk import log


class Command(BaseCommand):
    help = 'Update the specified raspi resources.'

    def add_arguments(self, parser):
        parser.add_argument('-r', '--resource', help='resource to update')

    def handle(self, *args, **opts):
        if opts['resource'] in [None, 'weather']: self._update_weather()
        if opts['resource'] in [None, 'calendar']: self._update_calendar()
        if opts['resource'] in [None, 'news']: self._update_news()

    @cached()
    def _update_weather(self):
        try:
            response = requests.get(settings.RASPI_WU_URL)
            return response.json()
        except Exception as err:
            log.exception(err)

    @cached()
    def _update_calendar(self):
        try:
            response = get_events(settings.RASPI_CALENDAR_URL)
            return response
        except Exception as err:
            log.exception(err)

    @cached()
    def _update_news(self):
        return None
