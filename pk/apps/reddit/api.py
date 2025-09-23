# encoding: utf-8
import logging, praw
from concurrent import futures
from django.conf import settings
from django.views.decorators.cache import cache_page
from ninja import Router
from ninja.decorators import decorate_view
from pk.utils import utils
from .schemas import RedditNews
log = logging.getLogger(__name__)
router = Router()


@router.get('/reddit/news', response=RedditNews, exclude_unset=True, url_name='note')
@decorate_view(cache_page(0 if settings.DEBUG else 1800))
def news(request):
    """ Get news from various Reddit subreddits using PRAW.
        Returns results in flat random order.
        https://praw.readthedocs.io/en/latest/code_overview/reddit_instance.html
    """
    reddit = praw.Reddit(**settings.REDDIT)
    subreddits = [
        {'subreddit':'news', 'count':15},
        {'subreddit':'technology', 'count':15},
        {'subreddit':'worldnews', 'count':15},
        {'subreddit':'boston', 'count':10},
        {'subreddit':'jokes', 'count':15},
    ]
    posts = []
    with futures.ThreadPoolExecutor(max_workers=5) as pool:
        promises = {pool.submit(_get_subreddit_items, s):s for s in subreddits}
        for future in futures.as_completed(promises):
            sub = promises[future]
            posts[sub['subreddit']] = future.result()
    return Response(items)


def _get_subreddit_items(reddit, subreddit, count):
    substories = []
    for post in reddit.subreddit(subreddit).top('day', limit=count*2):
        if _bad_domain(subreddit, post): continue
        # Clenaup and add this story to the return set
        story = {attr.replace('.','_'):utils.rget(post,attr) for attr in REDDIT_ATTRS}
        story['subreddit'] = subreddit
        story['redditurl'] = 'https://reddit.com%s' % story['permalink']
        story['url'] = 'https://reddit.com%s' % story['permalink']
        if 'reddit' not in story['domain'].replace('.',''):
            story['url'] = LUCKY_URL.format(**story)
        # If this is from r/jokes; make sure we have the punchline
        if subreddit == 'jokes' and (len(story['title']) > 100 or len(story['selftext']) > 100 or not story['selftext']):
            continue
        substories.append(story)
    return sorted(substories, key=lambda x:x['score'], reverse=True)[:count]
