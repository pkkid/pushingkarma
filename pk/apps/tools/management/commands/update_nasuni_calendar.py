#!/usr/bin/env python
# encoding: utf-8
from django.conf import settings
from django.core.management.base import BaseCommand
from ...calendar import get_events
from pk.utils import auth, rget


class Command(BaseCommand):
    help = 'Updates Nasuni Calendar on Google'

    def handle(self, *args, **kwargs):
        # o365_events = get_events(settings.OFFICE365_HTMLCAL)
        # for event in o365_events:
        #     print('---')
        #     print(f'Subject: {rget(event, "Subject", "")}')
        #     print(f'Location: {rget(event, "Location.DisplayName", "")}')
        #     print(f'Time: {rget(event, "Start", "")} - {rget(event, "End", "")}')

        service = auth.get_gauth_service(settings.EMAIL, 'calendar', 'v3')
        result = service.calendarList().list().execute()
        print(result)
