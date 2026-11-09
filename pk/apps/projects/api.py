# encoding: utf-8
import logging
from django.shortcuts import get_object_or_404
from ninja import Path, Router
from typing import List
from .models import GithubRepo
from .schemas import RepoSchema, RepoDetailSchema
log = logging.getLogger(__name__)
router = Router()


@router.get('/repos', response=List[RepoSchema])
def list_repos(request):
    """ List GitHub stats for all synced project repos, without commit history. """
    return GithubRepo.objects.defer('commits', 'contributors').order_by('-stars', 'name')


@router.get('/repos/{owner}/{name}', response=RepoDetailSchema, url_name='repo')
def get_repo(request,
      owner: str=Path(..., description='GitHub owner of the repo'),
      name: str=Path(..., description='GitHub repo name')):
    """ Get GitHub stats and daily commit counts for a single repo. """
    return get_object_or_404(GithubRepo, name=f'{owner}/{name}')
