#!/usr/bin/env python
# encoding: utf-8
import praw, random, requests
from django.conf import settings
from pk import log, utils
from pk.apps.calendar.views import get_events
from pk.utils import auth, context, threaded
from pk.utils.decorators import softcache, login_or_apikey_required

DISABLE_CACHE = False
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
REDDIT_ATTRS = ['title', 'author.name', 'score', 'permalink', 'domain', 'created_utc']


@login_or_apikey_required
def focus(request, tmpl='focus.html'):
    data = context.core(request)
    if request.GET.get('json'):
        data.update(threaded(
            weather=[_get_weather, [request]],
            calendar=[_get_calendar, [request]],
            news=[_get_news, [request]],
            tasks=[_get_tasks, [request]],
        ))
    data.cls = request.GET.get('cls', 'newtab')
    return utils.response(request, tmpl, data)


@softcache(timeout=1800, key='focus-weather', force=DISABLE_CACHE)
def _get_weather(request):
    try:
        response = requests.get(settings.FOCUS_WU_URL)
        return response.json()
    except Exception as err:
        log.exception(err)


@softcache(timeout=900, key='focus-calendar', force=DISABLE_CACHE)
def _get_calendar(request):
    try:
        return get_events(settings.FOCUS_CALENDAR_URL)
    except Exception as err:
        log.exception(err)


@softcache(timeout=300, key='focus-tasks', force=DISABLE_CACHE)
def _get_tasks(request):
    try:
        service = auth.get_gauth_service(settings.EMAIL, 'tasks')
        tasklists = service.tasklists().list().execute()
        tasklists = {tlist['title']:tlist for tlist in tasklists['items']}
        tasklist = tasklists['My Tasks']
        tasks = service.tasks().list(tasklist=tasklist['id']).execute()
        tasks = sorted(tasks['items'], key=lambda x:x['position'])
        return tasks
    except Exception as err:
        log.exception(err)


@softcache(timeout=1800, key='focus-news', force=DISABLE_CACHE)
def _get_news(request):
    try:
        reddit = praw.Reddit(**settings.REDDIT_ACCOUNT)
        stories = threaded(
            news=[_get_subreddit_items, [reddit, 'news', 10]],
            technology=[_get_subreddit_items, [reddit, 'technology', 10]],
            worldnews=[_get_subreddit_items, [reddit, 'worldnews', 10]],
            boston=[_get_subreddit_items, [reddit, 'boston', 10]],
        )
        # return a flat shuffled list
        stories = [item for sublist in stories.values() for item in sublist]
        random.shuffle(stories)
        return stories
    except Exception as err:
        log.exception(err)


def _get_subreddit_items(reddit, subreddit, count):
    substories = []
    limit = count * 2
    for post in reddit.subreddit(subreddit).top('day', limit=limit):
        if 'self.' not in post.domain:
            story = {attr.replace('.','_'):utils.rget(post,attr) for attr in REDDIT_ATTRS}
            story['subreddit'] = subreddit
            substories.append(story)
        substories = sorted(substories, key=lambda x:x['score'], reverse=True)[:limit]
    return substories
