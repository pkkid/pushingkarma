#!/usr/bin/env python
# encoding: utf-8
import argparse, requests
from django.conf import settings
from pk import log

# Weather Underground Settings
WU_APIKEY = getattr(settings, 'RASPI_WUNDERGROUND_APIKEY', '')
WU_LOCATION = getattr(settings, 'RASPI_WUNDERGROUND_LOCATION', '')
WU_URL = 'http://api.WU.com/api/%(apikey)s/conditions/forecast10day/astronomy/q/%(location)s.json'


def update_weather():
    try:
        url = WU_URL % {'apikey':WU_APIKEY, 'location':WU_LOCATION}
        response = requests.get(url)
        print(response.json)
    except Exception as err:
        log.exception(err)


def update_calendar():
    pass


def update_news():
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Update raspi metadata')
    parser.add_argument('-r', '--resource', help='resource to update')
    opts = parser.parse_args()
    if opts.resource in [None, 'weather']: update_weather()
    if opts.resource in [None, 'calendar']: update_calendar()
    if opts.resource in [None, 'news']: update_news()
