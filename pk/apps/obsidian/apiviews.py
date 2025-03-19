# encoding: utf-8
import glob, logging, re
from django.conf import settings
from django.views.decorators.cache import cache_page
from os.path import basename, getmtime, join
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
log = logging.getLogger(__name__)

@api_view(['get'])
@permission_classes([AllowAny])
def note(request, *args, **kwargs):
    """ Return the content of an obsidian note.
        • path: Path of note in the group vault (required)
        • group: Name of Obsidian group in settings.py (required)
    """
    try:
        path = request.query_params.get('path')
        groupname = request.query_params.get('group')
        if not path: path, groupname = _getFirstNote(request)
        group = settings.OBSIDIAN_NOTES[groupname]
        public = group.get('public', False)
        if public or request.user.is_authenticated:
            filepath = join(group['root'], path)
            with open(filepath, 'r', encoding='utf-8') as handle:
                content = handle.read()
            return Response({
                'vault': group['vault'],
                'path': path,
                'title': basename(filepath)[:-3],
                'content': content,
                'mtime': int(getmtime(filepath)),
                'public': public,
            })
    except Exception as err:
        log.exception(err)
    return Response({'error': 'Unknown note path or group.'}, status=404)


def _getFirstNote(request):
    """ Return the first note from an empty search. """
    note = search(request._request).data['results'][0]
    return note['path'], note['group']


@api_view(['get'])
@cache_page(300)
@permission_classes([AllowAny])
def search(request, *args, **kwargs):
    """ Search obsidian notes. This will open every note and count the number
        of times the search query word appears in the title and content. The results
        are sorted by count and mtime, and returned as a list of dictionaries.
        • search: search query string
    """
    try:
        results = {}
        query = request.query_params.get('search', '')
        query = re.sub(r'[^a-zA-Z0-9\s]', '', query[:100])  # light sanitization
        words = query.lower().split()
        for groupname, group in settings.OBSIDIAN_NOTES.items():
            public = group.get('public', False)
            if public or request.user.is_authenticated:
                for filepath in glob.glob(join(group['root'], '**', '*.md'), recursive=True):
                    path = filepath.replace(group['root'], '')
                    title = basename(filepath)[:-3]
                    score = sum(title.lower().count(word) for word in words) * 1000
                    with open(filepath, 'r', encoding='utf-8') as handle:
                        content = handle.read().lower()
                        score += sum(content.count(word) for word in words)
                    results[title] = {
                        'vault': group['vault'],
                        'group': groupname,
                        'path': path.lstrip('/'),
                        'title': title,
                        'mtime': int(getmtime(filepath)),
                        'public': public,
                        'score': score,
                    }
        results = sorted(results.values(), key=lambda x: (-x['score'], -x['mtime']))
        results = [x for x in results if x['score'] > 0] if query != '' else results
        return Response({'results': results})
    except Exception as err:
        log.exception(err)
    return Response({'error': 'Search failed.'}, status=500)
