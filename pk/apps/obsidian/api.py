# encoding: utf-8
import glob
from os.path import basename, dirname, getmtime, join
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

NOTES_DIR = f'{dirname(__file__)}/notes'


@api_view(['get'])
@permission_classes([AllowAny])
def search(request, *args, **kwargs):
    results = {}
    query = request.query_params.get('search', '')
    words = query.lower().split()
    for filepath in glob.glob(join(NOTES_DIR, '**', '*.md'), recursive=True):
        title = basename(filepath)[:-3]
        titlelower = title.lower()
        count = sum(titlelower.count(word) for word in words) * 1000
        with open(filepath, 'r', encoding='utf-8') as handle:
            content = handle.read().lower()
            count += sum(content.count(word) for word in words)
        results[title] = {'title':title, 'count':count, 'mtime':int(getmtime(filepath))}
    results = sorted(results.values(), key=lambda x: (-x['count'], -x['mtime']))
    results = [x for x in results if x['count'] > 0] if query != '' else results
    return Response(results)


@api_view(['get'])
@permission_classes([AllowAny])
def note(request, *args, **kwargs):
    return Response({})
