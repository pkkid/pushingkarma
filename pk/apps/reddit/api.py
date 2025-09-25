# encoding: utf-8
import hashlib, json, logging, praw, re
from concurrent import futures
from datetime import datetime
from django.conf import settings
from django.core.cache import cache
from ninja import Body, Router
from pk.utils import utils
from .schemas import NewsRequestSchema, NewsResponseSchema
log = logging.getLogger(__name__)
router = Router()

BLOCKED_DOMAINS = ['i.redd.it', 'imgur.com']
LUCKY_URL = 'http://google.com/search?btnI=I%27m+Feeling+Lucky&sourceid=navclient&q={domain}%20{title}'
REDDIT_ATTRS = ['title','score','permalink','domain','created_utc','selftext']


@router.post('/news', response=NewsResponseSchema, exclude_unset=True)
def news(request,
      data: NewsRequestSchema=Body(..., description='List of subreddit queries')):
    """ Get news from various Reddit subreddits. Example request:
        {"queries": [
            {"subreddit":"technology", "count":15},
            {"subreddit":"news", "count":10, "maxtitle":100, "mintext":10, "maxtext":100}
        ]}
    """
    # Create cache key based on request data and check we have a cached value.
    queries_json = json.dumps([query.dict() for query in data.queries], sort_keys=True)
    cache_key = f"reddit_news_{hashlib.md5(queries_json.encode()).hexdigest()}"
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    # No cached value, send request to Reddit
    subreddit_posts = {}
    queries = [query.dict() for query in data.queries]
    reddit = praw.Reddit(**settings.REDDIT_AUTH)
    log.info(f'Fetching posts for {len(queries)} subreddits.')
    with futures.ThreadPoolExecutor(max_workers=5) as pool:
        promises = {pool.submit(_get_subreddit_posts, reddit, **q):q['subreddit'] for q in queries}
        for future in futures.as_completed(promises):
            subreddit = promises[future]
            subreddit_posts[subreddit] = future.result()
    posts = [post for sublist in subreddit_posts.values() for post in sublist]
    posts = sorted(posts, key=lambda x:x['score'], reverse=True)
    result = {'posts': posts}
    # Cache for 15 minutes (900 seconds), skip caching in debug mode
    if not settings.DEBUG:
        cache.set(cache_key, result, 900)
    return result


def _get_subreddit_posts(reddit, subreddit, count=30, maxtitle=9999, mintext=0, maxtext=9999):
    """ Get posts from a specific subreddit. Setting mintext=0 will disallow self posts.
        https://praw.readthedocs.io/en/latest/code_overview/reddit_instance.html
    """
    posts = []
    for post in reddit.subreddit(subreddit).top('day', limit=count*2):
        if _blocked_domain(subreddit, post, mintext == 0):
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


def _blocked_domain(subreddit, post, blockself=True):
    """ Check the subreddit post domain against a list of blocked domains. """
    for regex in BLOCKED_DOMAINS:
        if re.findall(regex, post.domain):
            return True
    if blockself and re.findall(r'^self\.', post.domain):
        return True
    return False
