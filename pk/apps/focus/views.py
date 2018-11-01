#!/usr/bin/env python
# encoding: utf-8
import flickrapi, json, praw, random, requests
from django.conf import settings
from django.shortcuts import redirect
from pk import log, utils
from pk.apps.calendar.views import get_events
from pk.utils import auth, context, threaded
from pk.utils.decorators import softcache, login_or_apikey_required

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
FLICKR_GROUPID = '830711@N25'  # Best Landscape Photographers
FLICKR_EXTRAS = 'description,owner_name,url_h,geo'
FLICKER_PAGESIZE = 500
REDDIT_ATTRS = ['title','author.name','score','permalink','domain','created_utc']
GOOGLE_URL = 'https://www.google.com/search?q={q}'
LUCKY_URL = 'http://google.com/search?btnI=I%27m+Feeling+Lucky&sourceid=navclient&q={domain}%20{title}'


@login_or_apikey_required
def focus(request, id='newtab', tmpl='focus.html'):
    if request.GET.get('q'):
        return redirect(GOOGLE_URL.format(q=request.GET['q']))
    data = context.core(request, id=id)
    data.data = threaded(
        photo=[_get_photo, [request]],
        weather=[_get_weather, [request]],
        calendar=[_get_calendar, [request]],
        news=[_get_news, [request]],
        tasks=[_get_tasks, [request]],
    )
    return utils.response(request, tmpl, data)


@login_or_apikey_required
def raspi(request):
    return focus(request, id='raspi')


@softcache(timeout=64800, expires=2592000, key='focusphoto')
def _get_photo(request):
    """ Get a new background image from Flickr.
        https://www.flickr.com/services/api/flickr.galleries.getPhotos.html
        https://stuvel.eu/flickrapi-doc/
    """
    try:
        flickr = flickrapi.FlickrAPI(**settings.FLICKR)
        # Find number of pages in photo gallery
        response = flickr.groups.pools.getPhotos(group_id=FLICKR_GROUPID, per_page=FLICKER_PAGESIZE)
        pages = json.loads(response.decode('utf8'))['photos']['pages']
        # Choose a random photo from the gallery
        response = flickr.groups.pools.getPhotos(group_id=FLICKR_GROUPID, per_page=FLICKER_PAGESIZE,
            page=random.randrange(pages), get_user_info=1, extras=FLICKR_EXTRAS)
        photos = list(filter(_filter_photos, json.loads(response.decode('utf8'))['photos']['photo']))
        return random.choice(photos)
    except Exception as err:
        log.exception(err)


def _filter_photos(photo):
    if not photo.get('url_h'): return False
    if int(photo.get('width_h',0)) < int(photo.get('height_h',0)): return False
    return True


@softcache(timeout=1800, key='focusweather')
def _get_weather(request):
    """ Get weather information from Weather Underground.
        https://www.wunderground.com/weather/api/d/docs
    """
    try:
        response = requests.get(settings.WEATHERUNDERGROUND_URL)
        return response.json()
    except Exception as err:
        log.exception(err)


@softcache(timeout=900, key='focuscalendar')
def _get_calendar(request):
    """ Get calendar information from Office365. """
    try:
        return get_events(settings.OFFICE365_HTMLCAL)
    except Exception as err:
        log.exception(err)


@softcache(timeout=300, key='focustasks')
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


@softcache(timeout=1800, key='focusnews')
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
            story['redditurl'] = 'https://reddit.com%s' % story['permalink']
            story['url'] = 'https://reddit.com%s' % story['permalink']
            if 'reddit' not in story['domain'].replace('.',''):
                story['url'] = LUCKY_URL.format(**story)
            substories.append(story)
        substories = sorted(substories, key=lambda x:x['score'], reverse=True)[:limit]
    return substories
