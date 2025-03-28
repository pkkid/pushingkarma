# encoding: utf-8
import glob, logging, re
from django.conf import settings
from django.urls import reverse
from django.views.decorators.cache import cache_page
from ninja import Router
from ninja.decorators import decorate_view
from ninja.errors import HttpError
from ninja.pagination import paginate, PageNumberPagination
from os.path import basename, exists, getmtime, join
from typing import List, Optional
from pk import utils
from .schemas import NoteSchema
log = logging.getLogger(__name__)
router = Router()


@router.get('/notes', response=List[NoteSchema], exclude_unset=True)
@paginate(PageNumberPagination)
@decorate_view(cache_page(0 if settings.DEBUG else 300))
def list_notes(request, search:Optional[str]=''):
    """ Lists obsidian notes in the defined groups from settings. When searching,
        each word in the search string is counted in the content and title to give
        a score for sorting the results. The results are sorted by count and mtime,
        and returned as a list of dictionaries.
        • search (str): search query string.
    """
    results = []
    search = re.sub(r'[^a-zA-Z0-9\s]', '', search[:100])
    words = search.lower().split()
    for bucketname, bucket in settings.OBSIDIAN_BUCKETS.items():
        check_permission = bucket.get('check_permission', lambda user: True)
        if check_permission(request.user):
            for filepath in glob.glob(join(bucket['path'], '**', '*.md'), recursive=True):
                with open(filepath, 'r', encoding='utf-8') as handle:
                    content = handle.read().lower()
                path = filepath.replace(bucket['path'], '').lstrip('/')
                title = basename(filepath)[:-3]
                score = sum(title.lower().count(word) for word in words) * 1000
                score += sum(content.lower().count(word) for word in words)
                results.append(dict(
                    url = utils.reverse(request, 'api:note', bucketname=bucketname, path=path),
                    bucket = bucketname,
                    vault = bucket['vault'],
                    path = path,
                    title = title,
                    mtime = int(getmtime(filepath)),
                    score = score,
                ))
    results = [r for r in results if r.score > 0] if search != '' else results
    return sorted(results, key=lambda r: (-r['score'],-r['mtime']))


@router.get('/notes/{bucketname}/{path}', response=NoteSchema, exclude_unset=True, url_name='note')
def get_note(request, bucketname:str, path:str):
    """ Returns a single note from the obsian vault. The path is relative to the
        vault bucket. The bucketname is the name of the group in settings.py.
        • bucket: Name of Obsidian bucket in settings.py (required)
        • path: Path of note in the bucket vault (required)
    """
    if bucketname not in settings.OBSIDIAN_BUCKETS:
        raise HttpError(404, 'Unknown bucket name.')
    bucket = settings.OBSIDIAN_BUCKETS[bucketname]
    public = bucket.get('public', False)
    if public or request.user.is_authenticated:
        filepath = join(bucket['path'], path)
        if not exists(filepath):
            raise HttpError(404, 'Unknown note path.')
        with open(filepath, 'r', encoding='utf-8') as handle:
            content = handle.read()
        return dict(
            url = utils.reverse(request, 'api:note', bucketname=bucketname, path=path),
            bucket = bucketname,
            vault = bucket['vault'],
            path = path,
            title = basename(filepath)[:-3],
            content = content,
            mtime = int(getmtime(filepath)),
            public = public,
        )


# --------------------------------------------
# import glob, logging, re
# from django.conf import settings
# from django.views.decorators.cache import cache_page
# from os.path import basename, getmtime, join
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import AllowAny
# from rest_framework.response import Response
# log = logging.getLogger(__name__)

# @api_view(['get'])
# @permission_classes([AllowAny])
# def note(request, *args, **kwargs):
#     """ Return the content of an obsidian note.
#         • path: Path of note in the group vault (required)
#         • group: Name of Obsidian group in settings.py (required)
#     """
#     try:
#         path = request.query_params.get('path')
#         groupname = request.query_params.get('group')
#         if not path: path, groupname = _getFirstNote(request)
#         group = settings.OBSIDIAN_NOTES[groupname]
#         public = group.get('public', False)
#         if public or request.user.is_authenticated:
#             filepath = join(group['root'], path)
#             with open(filepath, 'r', encoding='utf-8') as handle:
#                 content = handle.read()
#             return Response({
#                 'vault': group['vault'],
#                 'path': path,
#                 'title': basename(filepath)[:-3],
#                 'content': content,
#                 'mtime': int(getmtime(filepath)),
#                 'public': public,
#             })
#     except Exception as err:
#         log.exception(err)
#     return Response({'error': 'Unknown note path or group.'}, status=404)


# def _getFirstNote(request):
#     """ Return the first note from an empty search. """
#     note = search(request._request).data['results'][0]
#     return note['path'], note['group']


# @api_view(['get'])
# @cache_page(300)
# @permission_classes([AllowAny])
# def search(request, *args, **kwargs):
#     """ Search obsidian notes. This will open every note and count the number
#         of times the search query word appears in the title and content. The results
#         are sorted by count and mtime, and returned as a list of dictionaries.
#         • search: search query string
#     """
#     try:
#         results = {}
#         query = request.query_params.get('search', '')
#         query = re.sub(r'[^a-zA-Z0-9\s]', '', query[:100])  # light sanitization
#         words = query.lower().split()
#         for groupname, group in settings.OBSIDIAN_NOTES.items():
#             public = group.get('public', False)
#             if public or request.user.is_authenticated:
#                 for filepath in glob.glob(join(group['root'], '**', '*.md'), recursive=True):
#                     path = filepath.replace(group['root'], '')
#                     title = basename(filepath)[:-3]
#                     score = sum(title.lower().count(word) for word in words) * 1000
#                     with open(filepath, 'r', encoding='utf-8') as handle:
#                         content = handle.read().lower()
#                         score += sum(content.count(word) for word in words)
#                     results[title] = {
#                         'vault': group['vault'],
#                         'group': groupname,
#                         'path': path.lstrip('/'),
#                         'title': title,
#                         'mtime': int(getmtime(filepath)),
#                         'public': public,
#                         'score': score,
#                     }
#         results = sorted(results.values(), key=lambda x: (-x['score'], -x['mtime']))
#         results = [x for x in results if x['score'] > 0] if query != '' else results
#         return Response({'results': results})
#     except Exception as err:
#         log.exception(err)
#     return Response({'error': 'Search failed.'}, status=500)
