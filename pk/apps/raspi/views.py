#!/usr/bin/env python
# encoding: utf-8
import json
from django.core.cache import cache
from pk import utils
from pk.utils import context

import pprint

def raspi(request, tmpl='raspi.html'):
    data = context.core(request)
    data.weather = json.loads(cache.get('raspi-weather', '{}'))
    data.calendar = json.loads(cache.get('raspi-calendar', '{}'))
    data.news = json.loads(cache.get('raspi-news', '{}'))
    pprint.pprint(data.weather)
    return utils.response(request, tmpl, data)
