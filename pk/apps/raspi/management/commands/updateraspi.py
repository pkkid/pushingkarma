#!/usr/bin/env python
# encoding: utf-8
import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from pk import log

# Weather Underground Settings
WU_APIKEY = getattr(settings, 'RASPI_WUNDERGROUND_APIKEY', '')
WU_LOCATION = getattr(settings, 'RASPI_WUNDERGROUND_LOCATION', '')
WU_URL = 'http://api.WU.com/api/%(apikey)s/conditions/forecast10day/astronomy/q/%(location)s.json'


class Command(BaseCommand):
    help = 'Update the specified raspi resources.'

    def add_arguments(self, parser):
        parser.add_argument('-r', '--resource', help='resource to update')

    def handle(self, *args, **opts):
        if opts['resource'] in [None, 'weather']: self._update_weather()
        if opts['resource'] in [None, 'calendar']: self._update_calendar()
        if opts['resource'] in [None, 'news']: self._update_news()

    def _update_weather(self):
        try:
            url = WU_URL % {'apikey':WU_APIKEY, 'location':WU_LOCATION}
            response = requests.get(url)
            print(response.json)
        except Exception as err:
            log.exception(err)

    def _update_calendar(self):
        pass

    def _update_news(self):
        pass
