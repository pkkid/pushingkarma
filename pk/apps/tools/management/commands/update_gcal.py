#!/usr/bin/env python
# encoding: utf-8
# https://developers.google.com/calendar/v3/reference/events/update
# http://googleapis.github.io/google-api-python-client/docs/dyn/calendar_v3.events.html
import hashlib, logging
from django.conf import settings
from django.core.management.base import BaseCommand
from ...o365 import get_o365_events
from pk.utils import auth
from pk.utils.decorators import log_exception
log = logging.getLogger('cmd')


class Command(BaseCommand):
    help = 'Update Nasuni Google Calendar'

    @log_exception(log)
    def handle(self, *args, **kwargs):
        """ Update Nasuni Google Calendar """
        log.info('---')
        log.info('Update Nasuni Google Calendar')
        service = auth.get_gauth_service(settings.EMAIL, 'calendar', 'v3')
        calendar = self.get_gcal(service, 'Nasuni')
        gcal_events = self.get_gcal_events(service, calendar)
        o365_events = self.get_o365_events(settings.OFFICE365_HTMLCAL)
        # Add New events from Office 365 to Google Calendar
        for o365_id, o365_event in o365_events.items():
            if o365_id not in gcal_events:
                log.info(f'Creating Event: {o365_event["Subject"]} - {o365_event["Start"][:10]}')
                gcal_event = self.create_gcal_event(o365_event, id=o365_id)
                service.events().insert(calendarId=calendar['id'], body=gcal_event).execute()
        # Remove or Modify existing events in Google Calendar
        for gcal_id, gcal_event in gcal_events.items():
            o365_event = o365_events.get(gcal_id)
            if not o365_event:
                log.info(f'Removing Event: {gcal_event["summary"]} - {gcal_event["start"]["dateTime"][:10]}')
                service.events().delete(calendarId=calendar['id'], eventId=gcal_id).execute()
                continue
            updates = self.check_update_event(gcal_event, o365_event)
            if updates:
                log.info(f'Updating Event: {gcal_event["summary"]} - {gcal_event["start"]["dateTime"][:10]}')
                service.events().update(calendarId=calendar['id'], eventId=gcal_id, body=updates).execute()

    def get_o365_events(self, calendar):
        """ Returns a dict of o365 Events {eventids: event} for the specified calendar. """
        _eventid = lambda event: hashlib.md5(event['ItemId']['Id'].encode()).hexdigest()
        return {_eventid(event):event for event in get_o365_events(calendar)}

    def get_gcal(self, service, name):
        """ Returns a dict object representing the specified Google Calendar. """
        result = service.calendarList().list().execute()
        for calendar in result['items']:
            if calendar['summary'].lower() == name.lower():
                return calendar
        raise Exception(f'Unknown calendar {name}')

    def get_gcal_events(self, service, calendar):
        """ Returns a dict of Google Calendar {eventids: event} for the specified calendar. """
        result = service.events().list(maxResults=999, calendarId=calendar['id']).execute()
        return {event['id']:event for event in result['items']}

    def create_gcal_event(self, o365_event, id=None):
        """ Return the dict required to create a Google Calendar event. """
        gcal_event = {'id':id} if id else {}
        gcal_event['summary'] = o365_event['Subject']
        gcal_event['location'] = o365_event['Location']['DisplayName']
        gcal_event['start'] = {'dateTime': o365_event['Start']}
        gcal_event['end'] = {'dateTime': o365_event['End']}
        return gcal_event

    def check_update_event(self, gcal_event, o365_event):
        """ Check we need to update the office365 event. """
        if (gcal_event['summary'] != o365_event['Subject']
          or gcal_event.get('location','') != o365_event['Location']['DisplayName']
          or gcal_event['start']['dateTime'] != o365_event['Start']
          or gcal_event['end']['dateTime'] != o365_event['End']):
            return self.create_gcal_event(o365_event)
        return None
