# encoding: utf-8
import praw, random, re, requests
from django.conf import settings
# from django.views.decorators.clickjacking import xframe_options_exempt
from pk import log, utils
from pk.apps.calendar.views import get_events
from pk.utils import auth, threaded
# from pk.utils.decorators import MINS, HOURS, DAYS
# from pk.utils.decorators import softcache, login_or_apikey_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .photos import get_album, PhotosFrom500px

REDDIT_ATTRS = ['title','author.name','score','permalink','domain','created_utc']
REDDIT_BADDOMAINS = ['i.redd.it', 'imgur.com', r'^self\.']
LUCKY_URL = 'http://google.com/search?btnI=I%27m+Feeling+Lucky&sourceid=navclient&q={domain}%20{title}'


@api_view()
@permission_classes([IsAuthenticated])
# @softcache(timeout=15*MINS, key='calendar')
def events(request):
    """ Get calendar events from Office365. """
    events = get_events(settings.OFFICE365_HTMLCAL)
    log.info(events)
    return Response(events)


@api_view()
# @softcache(timeout=30*MINS, key='news')
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


@api_view()
@permission_classes([IsAuthenticated])
# @softcache(timeout=18*HOURS, expires=30*DAYS, key='photo')
def photo(request):
    """ Get background photo information from the interwebs. """
    photos = get_album(request, cls=PhotosFrom500px)
    return Response(random.choice(photos))


@api_view()
@permission_classes([IsAuthenticated])
# @softcache(timeout=15*MINS, key='tasks')
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


@api_view()
@permission_classes([IsAuthenticated])
# @softcache(timeout=30*MINS, key='weather')
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
