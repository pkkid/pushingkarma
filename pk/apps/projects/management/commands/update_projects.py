# encoding: utf-8
""" Fetch repository stats and commit history from GitHub for the repos listed in
    settings.PROJECTS_GITHUB_REPOS. Commit history is fetched incrementally starting
    from the last day already stored, unless --full is passed. Set GITHUB_TOKEN in
    .env to avoid the 60 requests/hour limit for unauthenticated requests.
"""
import logging, os, requests
from collections import Counter
from django.conf import settings
from django.core.management.base import BaseCommand
from pk.apps.projects.models import GithubRepo
from pk.utils.logging import update_logging_filepath
log = logging.getLogger(__name__)

GITHUB_API = 'https://api.github.com'


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument('--loglevel', default='INFO', help='Console log level')
        parser.add_argument('--repos', help='Only update the specified repos (csv of owner/repo).')
        parser.add_argument('--full', action='store_true', help='Refetch the full commit history.')

    def handle(self, *args, **opts):
        # Setup logging and the GitHub session
        logging.getLogger().setLevel(opts['loglevel'])
        basename = os.path.basename(__file__).replace('.py', '')
        update_logging_filepath(f'{settings.LOGDIR}/{basename}.log')
        self.session = requests.Session()
        self.session.headers['Accept'] = 'application/vnd.github+json'
        if settings.GITHUB_TOKEN:
            self.session.headers['Authorization'] = f'Bearer {settings.GITHUB_TOKEN}'
        # Update each repo, logging failures so one bad repo does not stop the rest
        repos = opts['repos'].split(',') if opts['repos'] else settings.PROJECTS_GITHUB_REPOS
        for name in repos:
            try:
                self.update_repo(name, full=opts['full'])
            except Exception as err:
                log.exception(f'Error updating {name}: {err}')

    def update_repo(self, name, full=False):
        """ Fetch the latest stats and new commits for a single repo and save them. """
        repo = GithubRepo.objects.filter(name=name).first() or GithubRepo(name=name)
        info = self.get(f'/repos/{name}').json()
        repo.description = info['description']
        repo.homepage = info['homepage'] or None
        repo.language = info['language']
        repo.license = (info['license'] or {}).get('spdx_id')
        repo.stars = info['stargazers_count']
        repo.forks = info['forks_count']
        repo.issues = info['open_issues_count']
        repo.pushed = info['pushed_at']
        # Recount from the last stored day, since that day may have been partial
        commits = {} if full else dict(repo.commits)
        since = max(commits) if commits else None
        commits.pop(since, None)
        commits.update(self.get_commit_counts(name, since))
        repo.commits = dict(sorted(commits.items()))
        repo.save()
        log.info(f'Updated {name}: {repo.stars} stars, {sum(repo.commits.values())} commits')

    def get_commit_counts(self, name, since=None):
        """ Return {YYYY-MM-DD: count} for commits on the default branch. Commits are
            bucketed by committer date because that is the date the since filter uses.
        """
        counts = Counter()
        url, params = f'/repos/{name}/commits', {'per_page': 100}
        if since:
            params['since'] = f'{since}T00:00:00Z'
        while url:
            response = self.get(url, params, allow=(409,))
            # An empty repo returns 409 Conflict
            if response.status_code == 409:
                break
            for item in response.json():
                counts[item['commit']['committer']['date'][:10]] += 1
            url, params = response.links.get('next', {}).get('url'), None
        return dict(counts)

    def get(self, url, params=None, allow=()):
        """ GET a GitHub API url, raising on errors other than the allowed codes. """
        url = url if url.startswith('http') else f'{GITHUB_API}{url}'
        response = self.session.get(url, params=params, timeout=30)
        if response.status_code not in allow:
            response.raise_for_status()
        return response
