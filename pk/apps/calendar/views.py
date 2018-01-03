#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2018 PushingKarma. All rights reserved.
"""
import json, requests
from django.http import HttpResponse
from ics import Calendar, Event
from pk import log


def calendar(request, status=200):
    """ Convert o365 calendar events to ics because MS does it wrong. """
    try:
        url = request.GET.get('url')
        session = requests.Session()
        config, folders = _load_calendar(session, url)
        events = _load_events(session, url, config)
        ics = Calendar()
        for event in events:
            ics.events.append(Event(
                name=event['Subject'],
                location=event['Location']['DisplayName'],
                begin=event['Start'],
                end=event['End'],
            ))
        return HttpResponse(str(ics), content_type='text/calendar', status=status)
    except Exception as err:
        log.exception(err)


def _load_calendar(session, url):
    config, folders = None, None
    body = session.get(url).content.decode('utf8')
    for line in body.split('\n'):
        line = line.strip(' ')
        if line.startswith('PageDataPayload.owaUserConfig'):
            line = line.replace('PageDataPayload.owaUserConfig=', '')
            line = line.split(';')[0]
            config = json.loads(line)
        if line.startswith('PageDataPayload.calendarFolders'):
            line = line.replace('PageDataPayload.calendarFolders=', '')
            line = line.split(';')[0]
            folders = json.loads(line)
    return config, folders


def _load_events(session, url, config):
    service = url.replace('calendar.html', 'service.svc')
    response = session.post(service, data=_data(config), headers=_headers(url))
    events = json.loads(response.content.decode('utf8'))['Body']['ResponseMessages']['Items'][0]['RootFolder']['Items']
    return events


def _headers(url):
    anchor_mailbox = url.split('/')[5]
    return {
        'Action': 'FindItem', 'ID': '-1', 'AC': '1',
        'Content-Type': 'application/json; charset=UTF-8',
        'Host': 'outlook.office365.com',
        'Origin': 'https://outlook.office365.com',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',  # noqa
        'X-AnchorMailbox': anchor_mailbox,
        'X-OWA-ActionId': '-1',
        'X-OWA-ActionName': 'GetCalendarItemsAction_Month',
        'X-OWA-Attempt': '1',
        'X-OWA-CANARY': 'g-tE1GiI5E6WWEMp1lDla_BAl3ubUdUYu6hk9jTzoKy1ib_TcvPJnrplm1iU5_NM8hh_9oYupmk.',
        'X-OWA-ClientBegin': '2018-01-02T04:45:31.544',
        'X-OWA-ClientBuildVersion': '16.2080.5.2459088',
        'X-OWA-CorrelationId': 'A1AA550B559D43C387DB995A9EEDE008_151486833154404',
        'X-Requested-With': 'XMLHttpRequest',
    }


def _data(config):
    # Order matters here, not work making an ordered dict.
    return '{"__type":"FindItemJsonRequest:#Exchange",' \
        '"Header":{"__type":"JsonRequestHeaders:#Exchange",' \
        '  "RequestServerVersion":"Exchange2013",' \
        '  "TimeZoneContext":{"__type":"TimeZoneContext:#Exchange",' \
        '  "TimeZoneDefinition":{"__type":"TimeZoneDefinitionType:#Exchange",' \
        '  "Id":"Eastern Standard Time"}}},' \
        '"Body":{"__type":"FindItemRequest:#Exchange",' \
        '  "ItemShape":{"__type":"ItemResponseShape:#Exchange",' \
        '    "BaseShape":"IdOnly",' \
        '    "AdditionalProperties":[' \
        '      {"__type":"PropertyUri:#Exchange","FieldURI":"ItemParentId"},' \
        '      {"__type":"PropertyUri:#Exchange","FieldURI":"Sensitivity"},' \
        '      {"__type":"PropertyUri:#Exchange","FieldURI":"AppointmentState"},' \
        '      {"__type":"PropertyUri:#Exchange","FieldURI":"IsCancelled"},' \
        '      {"__type":"PropertyUri:#Exchange","FieldURI":"HasAttachments"},' \
        '      {"__type":"PropertyUri:#Exchange","FieldURI":"LegacyFreeBusyStatus"},' \
        '      {"__type":"PropertyUri:#Exchange","FieldURI":"CalendarItemType"},' \
        '      {"__type":"PropertyUri:#Exchange","FieldURI":"Start"},' \
        '      {"__type":"PropertyUri:#Exchange","FieldURI":"End"},' \
        '      {"__type":"PropertyUri:#Exchange","FieldURI":"IsAllDayEvent"},' \
        '      {"__type":"PropertyUri:#Exchange","FieldURI":"Organizer"},' \
        '      {"__type":"PropertyUri:#Exchange","FieldURI":"Subject"},' \
        '      {"__type":"PropertyUri:#Exchange","FieldURI":"IsMeeting"},' \
        '      {"__type":"PropertyUri:#Exchange","FieldURI":"UID"},' \
        '      {"__type":"PropertyUri:#Exchange","FieldURI":"InstanceKey"},' \
        '      {"__type":"PropertyUri:#Exchange","FieldURI":"ItemEffectiveRights"},' \
        '      {"__type":"PropertyUri:#Exchange","FieldURI":"JoinOnlineMeetingUrl"},' \
        '      {"__type":"PropertyUri:#Exchange","FieldURI":"ConversationId"},' \
        '      {"__type":"PropertyUri:#Exchange","FieldURI":"CalendarIsResponseRequested"},' \
        '      {"__type":"PropertyUri:#Exchange","FieldURI":"Categories"},' \
        '      {"__type":"PropertyUri:#Exchange","FieldURI":"IsRecurring"},' \
        '      {"__type":"PropertyUri:#Exchange","FieldURI":"IsOrganizer"},' \
        '      {"__type":"PropertyUri:#Exchange","FieldURI":"EnhancedLocation"},' \
        '      {"__type":"PropertyUri:#Exchange","FieldURI":"IsSeriesCancelled"},' \
        '      {"__type":"PropertyUri:#Exchange","FieldURI":"Charm"}]},' \
        '  "ParentFolderIds":[{' \
        '    "__type":"FolderId:#Exchange",' \
        '    "Id":"%(parentFolderId)s",' \
        '    "ChangeKey":"%(parentFolderChangeKey)s"}],' \
        '  "Traversal":"Shallow",' \
        '  "Paging":{"__type":"CalendarPageView:#Exchange",' \
        '    "StartDate":"2017-12-31T00:00:00.001",' \
        '    "EndDate":"2018-02-04T00:00:00.000"}' \
        '}}' % {
            'parentFolderId': config['SessionSettings']['DefaultFolderIds'][0]['Id'],
            'parentFolderChangeKey': config['SessionSettings']['DefaultFolderIds'][0]['ChangeKey'],
        }
