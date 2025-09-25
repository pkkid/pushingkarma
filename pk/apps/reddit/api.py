# encoding: utf-8
import logging, praw, re
from concurrent import futures
from datetime import datetime
from django.conf import settings
from django.views.decorators.cache import cache_page
from ninja import Body, Router
from ninja.decorators import decorate_view
from pk.utils import utils
from typing import List
from .schemas import RedditPostSchema, RedditNewsSchema
log = logging.getLogger(__name__)
router = Router()

BLOCKED_DOMAINS = ['i.redd.it', 'imgur.com', r'^self\.']
LUCKY_URL = 'http://google.com/search?btnI=I%27m+Feeling+Lucky&sourceid=navclient&q={domain}%20{title}'
REDDIT_ATTRS = ['title','score','permalink','domain','created_utc','selftext']


@router.post('/news', response=List[RedditPostSchema], exclude_unset=True)
@decorate_view(cache_page(0 if settings.DEBUG else 1800))
def news(request,
      data: RedditNewsSchema=Body(..., description='List of subreddit queries')):
    """ Get news from various Reddit subreddits. Example request:
        {"queries": [
            {"subreddit":"technology", "count":15},
            {"subreddit":"news", "count":10, "maxtitle":100, "mintext":10, "maxtext":100}
        ]}
    """
    subreddit_posts = {}
    queries = [query.dict() for query in data.queries]
    reddit = praw.Reddit(**settings.REDDIT_AUTH)
    with futures.ThreadPoolExecutor(max_workers=5) as pool:
        promises = {pool.submit(_get_subreddit_posts, reddit, **q):q['subreddit'] for q in queries}
        for future in futures.as_completed(promises):
            subreddit = promises[future]
            subreddit_posts[subreddit] = future.result()
    posts = [post for sublist in subreddit_posts.values() for post in sublist]
    posts = sorted(posts, key=lambda x:x['score'], reverse=True)
    return posts


def _get_subreddit_posts(reddit, subreddit, count=30, maxtitle=9999, mintext=0, maxtext=9999):
    """ Get posts from a specific subreddit.
        https://praw.readthedocs.io/en/latest/code_overview/reddit_instance.html
    """
    posts = []
    for post in reddit.subreddit(subreddit).top('day', limit=count*2):
        if _blocked_domain(subreddit, post):
            continue
        post = {attr.replace('.','_'):utils.rget(post,attr) for attr in REDDIT_ATTRS}
        post['subreddit'] = subreddit
        post['redditurl'] = f'https://reddit.com{post['permalink']}'
        post['created'] = datetime.fromtimestamp(post['created_utc'])
        post['url'] = f'https://reddit.com{post['permalink']}'
        if 'reddit' not in post['domain'].replace('.',''):
            post['url'] = LUCKY_URL.format(**post)
        if len(post['title']) > maxtitle or len(post['selftext']) < mintext or len(post['selftext']) > maxtext:
            continue
        posts.append(post)
    return sorted(posts, key=lambda x:x['score'], reverse=True)[:count]


def _blocked_domain(subreddit, post):
    """ Check the subreddit post domain against a list of blocked domains. """
    for regex in BLOCKED_DOMAINS:
        if re.findall(regex, post.domain):
            return True
    return False
