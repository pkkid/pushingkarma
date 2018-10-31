#!/usr/bin/env python
# encoding: utf-8
import flickrapi, json, os, praw, random, requests
import urllib.request
from django.conf import settings
from django.core.cache import cache
from pk import log, utils
from pk.apps.calendar.views import get_events
from pk.utils import auth, context, threaded
from pk.utils.decorators import softcache, login_or_apikey_required

DISABLE_CACHE = False
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
FLICKR_GROUPID = '830711@N25'  # Best Landscape Photographers
REDDIT_ATTRS = ['title', 'author.name', 'score', 'permalink', 'domain', 'created_utc']
# FLICKR_DOWNLOAD = os.path.join(settings.BASE_DIR, 'collectstatic/site/flickr.jpg')
# if settings.DEBUG:
#     FLICKR_DOWNLOAD = os.path.join(settings.BASE_DIR, 'static/site/img/flickr.jpg')


@login_or_apikey_required
def focus(request, id='newtab', tmpl='focus.html'):
    data = context.core(request, id=id)
    if request.GET.get('json'):
        data.update(threaded(
            background=[_get_background, [request]],
            weather=[_get_weather, [request]],
            calendar=[_get_calendar, [request]],
            news=[_get_news, [request]],
            tasks=[_get_tasks, [request]],
        ))
    if id == 'newtab':
        background = json.loads(cache.get('focus-background', '{}'))
        data.bgimg = background.get('data',{}).get('url_h','')
    return utils.response(request, tmpl, data)


@login_or_apikey_required
def raspi(request):
    return focus(request, id='raspi')


@softcache(timeout=64800, expires=2592000, key='focus-background', force=DISABLE_CACHE)
def _get_background(request):
    """ Get a new background image from Flickr.
        https://www.flickr.com/services/api/flickr.galleries.getPhotos.html
        https://stuvel.eu/flickrapi-doc/
    """
    try:
        flickr = flickrapi.FlickrAPI(**settings.FLICKR)
        # Find number of pages in photo gallery
        response = flickr.groups.pools.getPhotos(group_id=FLICKR_GROUPID, per_page=500)
        pages = json.loads(response)['photos']['pages']
        # Choose a random photo from the gallery
        response = flickr.groups.pools.getPhotos(group_id=FLICKR_GROUPID, per_page=500,
            page=random.randrange(pages), get_user_info=1, extras='url_h,geo')
        photos = list(filter(_filter_photos, json.loads(response)['photos']['photo']))
        photo = random.choice(photos)
        # Download the photo
        # log.info('Downloading new background: %s', photo['url_h'])
        # image = urllib.request.urlopen(photo['url_h'])
        # with open(FLICKR_DOWNLOAD, 'wb') as handle:
        #     handle.write(image.read())
        return photo
    except Exception as err:
        log.exception(err)


def _filter_photos(photo):
    if not photo.get('url_h'): return False
    if int(photo.get('width_h',0)) < int(photo.get('height_h',0)): return False
    return True


@softcache(timeout=1800, key='focus-weather', force=DISABLE_CACHE)
def _get_weather(request):
    """ Get weather information from Weather Underground.
        https://www.wunderground.com/weather/api/d/docs
    """
    try:
        response = requests.get(settings.WEATHERUNDERGROUND_URL)
        return response.json()
    except Exception as err:
        log.exception(err)


@softcache(timeout=900, key='focus-calendar', force=DISABLE_CACHE)
def _get_calendar(request):
    """ Get calendar information from Office365. """
    try:
        return get_events(settings.OFFICE365_HTMLCAL)
    except Exception as err:
        log.exception(err)


@softcache(timeout=300, key='focus-tasks', force=DISABLE_CACHE)
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
        tasks = sorted(tasks['items'], key=lambda x:x['position'])
        return tasks
    except Exception as err:
        log.exception(err)


@softcache(timeout=1800, key='focus-news', force=DISABLE_CACHE)
def _get_news(request):
    """ Get news from various Reddit subreddits using PRAW.
        https://praw.readthedocs.io/en/latest/code_overview/reddit_instance.html
    """
    try:
        reddit = praw.Reddit(**settings.REDDIT)
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
