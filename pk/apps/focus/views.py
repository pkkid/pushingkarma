#!/usr/bin/env python
# encoding: utf-8
import praw, random, re, requests
from django.conf import settings
from django.views.decorators.clickjacking import xframe_options_exempt
from pk import log, utils
from pk.apps.calendar.views import get_events
from pk.utils import auth, context, threaded
from pk.utils.decorators import MINS, HOURS, DAYS
from pk.utils.decorators import softcache, login_or_apikey_required
from .photos import get_album, PhotosFrom500px

REDDIT_ATTRS = ['title','author.name','score','permalink','domain','created_utc']
REDDIT_BADDOMAINS = ['i.redd.it', 'imgur.com', '^self\.']
LUCKY_URL = 'http://google.com/search?btnI=I%27m+Feeling+Lucky&sourceid=navclient&q={domain}%20{title}'


@xframe_options_exempt
@login_or_apikey_required
def focus(request, id='newtab', tmpl='focus.html'):
    data = context.core(request, id=id)
    data.data = threaded(
        photo=[_get_photo, request],
        weather=[_get_weather, request],
        calendar=[_get_calendar, request],
        news=[_get_news, request],
        tasks=[_get_tasks, request],
    )
    return utils.response(request, tmpl, data)


@login_or_apikey_required
def raspi(request):
    return focus(request, id='raspi')


@softcache(timeout=18*HOURS, expires=30*DAYS, key='photo')
def _get_photo(request):
    """ Get background photo information from the interwebs. """
    try:
        photos = get_album(request, cls=PhotosFrom500px)
        return random.choice(photos)
    except Exception as err:
        log.exception(err)


@softcache(timeout=30*MINS, key='weather')
def _get_weather(request):
    """ Get weather information from Weather Underground.
        https://www.wunderground.com/weather/api/d/docs
    """
    try:
        response = requests.get(settings.DARKSKY_URL)
        return response.json()
    except Exception as err:
        log.exception(err)


@softcache(timeout=15*MINS, key='calendar')
def _get_calendar(request):
    """ Get calendar information from Office365. """
    try:
        return get_events(settings.OFFICE365_HTMLCAL)
    except Exception as err:
        log.exception(err)


@softcache(timeout=15*MINS, key='tasks')
def _get_tasks(request):
    """ Get open tasks from Google Tasks.
        https://developers.google.com/tasks/v1/reference/
    """
    try:
        service = auth.get_gauth_service(settings.EMAIL, 'tasks')
        tasklists = service.tasklists().list().execute()
        tasklists = {tlist['title']:tlist for tlist in tasklists['items']}
        tasklist = tasklists['My Tasks']
        tasks = service.tasks().list(tasklist=tasklist['id']).execute()
        tasks = sorted(tasks.get('items',[]), key=lambda x:x['position'])
        return tasks
    except Exception as err:
        log.exception(err)


@softcache(timeout=30*MINS, key='news')
def _get_news(request):
    """ Get news from various Reddit subreddits using PRAW.
        https://praw.readthedocs.io/en/latest/code_overview/reddit_instance.html
    """
    try:
        reddit = praw.Reddit(**settings.REDDIT)
        stories = threaded(
            news=[_get_subreddit_items, reddit, 'news', 15],
            technology=[_get_subreddit_items, reddit, 'technology', 15],
            worldnews=[_get_subreddit_items, reddit, 'worldnews', 15],
            boston=[_get_subreddit_items, reddit, 'boston', 10],
        )
        # return a flat shuffled list
        stories = [item for sublist in stories.values() for item in sublist]
        return stories
    except Exception as err:
        log.exception(err)


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
    substories = sorted(substories, key=lambda x:x['score'], reverse=True)[:count]
    return substories
