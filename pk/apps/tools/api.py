# encoding: utf-8
import praw, random, re, requests
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from ics import Calendar, Event
from pk import log, utils
from pk.utils import auth, threaded
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .calendar import get_events
from .photos import get_album, PhotosFrom500px

REDDIT_ATTRS = ['title','author.name','score','permalink','domain','created_utc']
REDDIT_BADDOMAINS = ['i.redd.it', 'imgur.com', r'^self\.']
LUCKY_URL = 'http://google.com/search?btnI=I%27m+Feeling+Lucky&sourceid=navclient&q={domain}%20{title}'


@api_view(['get'])
def tools(request):
    root = reverse('api-root', request=request)
    return Response({
        'tools/events': f'{root}tools/events',
        'tools/ical': f'{root}tools/ical',
        'tools/news': f'{root}tools/news',
        'tools/photo': f'{root}tools/photo',
        'tools/tasks': f'{root}tools/tasks',
        'tools/weather': f'{root}tools/weather',
    })


@permission_classes([IsAuthenticated])
@cache_page(60*15)  # 15 minutes
def events(request):
    """ Get calendar events from Office365. """
    events = get_events(settings.OFFICE365_HTMLCAL)
    log.info(events)
    return Response(events)


@api_view(['get'])
@permission_classes([IsAuthenticated])
@cache_page(60*15)  # 15 minutes
def ical(request, status=200):
    """ Returns Office365 calendar events as ics because MS does it wrong. """
    url = request.GET.get('url', settings.OFFICE365_HTMLCAL)
    ics = Calendar()
    for event in get_events(url):
        ics.events.append(Event(
            name=event['Subject'],
            uid=event['ItemId']['Id'],
            location=event['Location']['DisplayName'],
            begin=event['Start'],
            end=event['End'],
        ))
    return HttpResponse(str(ics), content_type='text/calendar', status=status)


@api_view(['get'])
@cache_page(60*30)  # 30 minutes
def news(request):
    """ Get news from various Reddit subreddits using PRAW.
        Returns results in flat random order.
        https://praw.readthedocs.io/en/latest/code_overview/reddit_instance.html
    """
    reddit = praw.Reddit(**settings.REDDIT)
    stories = threaded(
        news=[_get_subreddit_items, reddit, 'news', 15],
        technology=[_get_subreddit_items, reddit, 'technology', 15],
        worldnews=[_get_subreddit_items, reddit, 'worldnews', 15],
        boston=[_get_subreddit_items, reddit, 'boston', 10],
    )
    return Response([item for sublist in stories.values() for item in sublist])


@api_view(['get'])
@permission_classes([IsAuthenticated])
@cache_page(60*60*18)  # 18 hours
def photo(request):
    """ Get background photo information from the interwebs. """
    photos = get_album(request, cls=PhotosFrom500px)
    return Response(random.choice(photos))


@api_view(['get'])
@permission_classes([IsAuthenticated])
@cache_page(60*15)  # 15 minutes
def tasks(request):
    """ Get open tasks from Google Tasks.
        https://developers.google.com/tasks/v1/reference/
    """
    service = auth.get_gauth_service(settings.EMAIL, 'tasks')
    tasklists = service.tasklists().list().execute()
    tasklists = {tlist['title']:tlist for tlist in tasklists['items']}
    tasklist = tasklists['My Tasks']
    tasks = service.tasks().list(tasklist=tasklist['id']).execute()
    return Response(sorted(tasks.get('items',[]), key=lambda x:x['position']))


@api_view(['get'])
@permission_classes([IsAuthenticated])
@cache_page(60*30)  # 30 minutes
def weather(request):
    """ Get weather information from Weather Underground.
        https://www.wunderground.com/weather/api/d/docs
    """
    return Response(requests.get(settings.DARKSKY_URL).json())


def _get_subreddit_items(reddit, subreddit, count):
    substories = []
    for post in reddit.subreddit(subreddit).top('day', limit=count*2):
        # Check this is a bad domain
        for regex in REDDIT_BADDOMAINS:
            if re.findall(regex, post.domain):
                continue
        # Clenaup and add this story to the return set
        story = {attr.replace('.','_'):utils.rget(post,attr) for attr in REDDIT_ATTRS}
        story['subreddit'] = subreddit
        story['redditurl'] = 'https://reddit.com%s' % story['permalink']
        story['url'] = 'https://reddit.com%s' % story['permalink']
        if 'reddit' not in story['domain'].replace('.',''):
            story['url'] = LUCKY_URL.format(**story)
        substories.append(story)
    return sorted(substories, key=lambda x:x['score'], reverse=True)[:count]
