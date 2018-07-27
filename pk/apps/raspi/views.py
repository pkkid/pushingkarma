#!/usr/bin/env python
# encoding: utf-8
from pk import utils
from pk.apps.calendar.views import get_events
from pk.settings.secrets import RASPI_CALENDAR_URL


def raspi(request, tmpl='raspi.html'):
    events = get_events(RASPI_CALENDAR_URL)
    events = [e for e in events if e['Start'].startswith('2018-07-02')]
    print(events)
    return utils.response(request, tmpl, {})
