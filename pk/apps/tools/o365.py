# encoding: utf-8
import re, requests
from datetime import datetime, timedelta
from pk import log, utils

DATEFORMAT = '%Y-%m-%dT00:00:00.000'


def get_events(public_calendar_url):
    """ Fetch events from the Office 365 public calendar url. This is the
        http URL found in Settings > Calendar > Shared Calendars > HTML.
    """
    session = requests.Session()
    caldata = _getAnonymousCalendarSessionData(session, public_calendar_url)
    events = _findItem(session, public_calendar_url, caldata)
    for i in range(len(events)):
        location = utils.rget(events[i], 'Location.DisplayName', '')
        location = location.replace(' Conference Room', '')
        location = re.sub(r'BOSHQ-\d+-', '', location)
        location = re.sub(r'MARMA-\d+-', '', location)
        # location = re.sub(r'https*://\w*\.zoom\.us/j/\d+', 'Zoom', location)
        events[i]['Location']['DisplayName'] = location
    return events


def _getAnonymousCalendarSessionData(session, url):
    """ Returns the sessiojn data needed to render this calendar. """
    headers = {
        'action': 'GetAnonymousCalendarSessionData',
        'x-owa-urlpostdata': '%7B%22__type%22%3A%22GetAnonymousCalendarSessionDataJsonRequest%3A%23'
          'Exchange%22%2C%22Header%22%3A%7B%22__type%22%3A%22JsonRequestHeaders%3A%23Exchange%22%2C%22'
          'RequestServerVersion%22%3A%22Exchange2015%22%2C%22TimeZoneContext%22%3A%7B%22__type%22%3A%22'
          'TimeZoneContext%3A%23Exchange%22%2C%22TimeZoneDefinition%22%3A%7B%22__type%22%3A%22TimeZoneDefinitionType%3A%23'
          'Exchange%22%2C%22Id%22%3A%22Pacific%20Standard%20Time%22%7D%7D%7D%7D',
    }
    url = url.replace('/calendar/published/', '/owa/calendar/')
    url = url.replace('/calendar.html', '/service.svc')
    log.info('Fetching caldata from %s', url)
    return session.post(url, headers=headers).json()


def _findItem(session, url, caldata):
    now = datetime.now()
    startdate = (now - timedelta(days=7)).strftime(DATEFORMAT)
    enddate = (now + timedelta(days=30)).strftime(DATEFORMAT)
    folderid = utils.rget(caldata, 'Body.CalendarFolder.FolderId.Id', None)
    headers = {
        'action': 'FindItem',
        'x-owa-urlpostdata': '%7B%22__type%22%3A%22FindItemJsonRequest%3A%23Exchange%22%2C%22Header%22%3A%7B%22__type%22%3A%22'
          'JsonRequestHeaders%3A%23Exchange%22%2C%22RequestServerVersion%22%3A%22Exchange2015%22%2C%22TimeZoneContext%22%3A%7B%22'
          '__type%22%3A%22TimeZoneContext%3A%23Exchange%22%2C%22TimeZoneDefinition%22%3A%7B%22__type%22%3A%22'
          'TimeZoneDefinitionType%3A%23Exchange%22%2C%22Id%22%3A%22Pacific%20Standard%20Time%22%7D%7D%7D%2C%22Body%22%3A%7B%22'
          '__type%22%3A%22FindItemRequest%3A%23Exchange%22%2C%22ParentFolderIds%22%3A%5B%7B%22__type%22%3A%22FolderId%3A%23'
          f'Exchange%22%2C%22Id%22%3A%22{folderid}%22%7D%5D%2C%22'
          'ItemShape%22%3A%7B%22__type%22%3A%22ItemResponseShape%3A%23Exchange%22%2C%22BaseShape%22%3A%22IdOnly%22%7D%2C%22Traversal%22%3A%22'
          'Shallow%22%2C%22Paging%22%3A%7B%22__type%22%3A%22CalendarPageView%3A%23Exchange%22%2C%22'
          f'StartDate%22%3A%22{startdate}%22%2C%22EndDate%22%3A%22{enddate}%22%7D%7D%7D',
    }
    url = url.replace('/calendar/published/', '/owa/calendar/')
    url = url.replace('/calendar.html', '/service.svc')
    log.info('Fetching events from %s', url)
    response = session.post(url, headers=headers).json()
    return utils.rget(response, 'Body.ResponseMessages.Items.0.RootFolder.Items', [])
