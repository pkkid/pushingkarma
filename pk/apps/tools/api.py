# encoding: utf-8
from datetime import datetime
import praw, random, re, requests
from django.conf import settings
from pk.utils.decorators import cache_api_data
from pk import utils
from pk.utils import threaded
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from . import o365, photos

REDDIT_ATTRS = ['title','author.name','score','permalink','domain','created_utc']
REDDIT_BADDOMAINS = ['i.redd.it', 'imgur.com', r'^self\.']
LUCKY_URL = 'http://google.com/search?btnI=I%27m+Feeling+Lucky&sourceid=navclient&q={domain}%20{title}'
AUTH_CLASSES = [SessionAuthentication, TokenAuthentication]
PERM_CLASSES = [IsAuthenticated]


def cached_api_view(methods, timeout, key=None):
    """ Convenience decorator to rule them all. """
    def wrapper1(func):
        cachekey = key or f'{func.__module__}.{func.__name__}'
        @api_view(methods)  # noqa
        @authentication_classes(AUTH_CLASSES)
        @permission_classes(PERM_CLASSES)
        @cache_api_data(timeout, cachekey)
        def wrapper2(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper2
    return wrapper1


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


@cached_api_view(['get'], 60*15)  # 15 minutes
def events(request):
    """ Get calendar events from Office365. """
    events = o365.get_events(settings.OFFICE365_HTMLCAL)
    return Response(events)


@cached_api_view(['get'], 60*30)  # 30 minutes
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


@cached_api_view(['get'], 60*60*18)  # 18 hours
def photo(request):
    """ Get background photo information from the interwebs. """
    return Response(random.choice(photos.get_album()))


@cached_api_view(['get'], 60*15)  # 15 minutes
def tasks(request):
    """ Get open tasks from Google Tasks.
        https://developers.google.com/tasks/v1/reference/
    """
    service = request.user.google_service('tasks')
    tasklists = service.tasklists().list().execute()
    tasklists = {tlist['title']:tlist for tlist in tasklists['items']}
    tasklist = tasklists['My Tasks']
    tasks = service.tasks().list(tasklist=tasklist['id']).execute()
    return Response(sorted(tasks.get('items',[]), key=lambda x:x['position']))


@cached_api_view(['get'], 60*15)  # 15 minutes
def weather(request):
    """ Get current weather information. """
    CODES = settings.OPENMETEO_WEATHERCODES
    weather = requests.get(settings.OPENMETEO_URL).json()
    weather['location'] = settings.OPENMETEO_LOCATION
    weather['current_weather']['text'] = CODES[weather['current_weather']['weathercode']]['text']
    weather['current_weather']['icon'] = CODES[weather['current_weather']['weathercode']]['icon']
    # Fix the daily weather format
    daily = []
    for i in range(len(weather['daily']['time'])):
        daily.append({})
        for key in weather['daily'].keys():
            daily[i][key] = weather['daily'][key][i]
            if key == 'weathercode':
                daily[i]['text'] = CODES[daily[i][key]]['text']
                daily[i]['icon'] = CODES[daily[i][key]]['icon']
    weather['daily'] = daily
    # Display a Moon icon if after sunset or before sunrise
    now = datetime.now().strftime('%Y-%m-%dT%H:%M')
    sunrise, sunset = daily[0]['sunrise'], daily[0]['sunset']
    if (now < sunrise or now > sunset):
        if weather['current_weather']['icon'] == 'sunny': weather['current_weather']['icon'] = 'night'
        if weather['current_weather']['icon'] == 'partly-cloudy': weather['current_weather']['icon'] = 'night-partly-cloudy'
    return Response(weather)


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


@api_view(['get'])
@permission_classes(PERM_CLASSES)
def error(request):
    raise Exception('Test API exception')
