# encoding: utf-8
import glob, logging, re
from django.conf import settings
from django.views.decorators.cache import cache_page
from ninja import Router
from ninja.decorators import decorate_view
from ninja.errors import HttpError
from os.path import basename, exists, getmtime, join
from pk.utils import PageSchema, paginate, reverse
from .schemas import NoteSchema
log = logging.getLogger(__name__)
router = Router()


@router.get('/notes/{bucketname}/{path}', response=NoteSchema, exclude_unset=True, url_name='note')
def get_note(request, bucketname:str, path:str):
    """ Returns a single note from the obsian vault. The path is relative to the
        vault bucket. The bucketname is the name of the group in settings.py.
        • bucketname: Name of Obsidian bucket in settings.py (required)
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
            url = reverse(request, 'api:note', bucketname=bucketname, path=path),
            bucket = bucketname,
            vault = bucket['vault'],
            path = path,
            title = basename(filepath)[:-3],
            content = content,
            mtime = int(getmtime(filepath)),
            public = public,
        )
    raise HttpError(403, 'Permission denied.')


@router.get('/notes', response=PageSchema(NoteSchema), exclude_unset=True)
@decorate_view(cache_page(0 if settings.DEBUG else 300))
def list_notes(request, search:str='', page:int=1):
    """ Lists obsidian notes in the defined groups from settings. When searching,
        each word in the search string is counted in the content and title to give
        a score for sorting the results. The results are sorted by count and mtime,
        and returned as a list of dictionaries.
        • search (str): search query string.
        • page: Page number of results to return
    """
    items = []
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
                items.append(dict(
                    url = reverse(request, 'api:note', bucketname=bucketname, path=path),
                    bucket = bucketname,
                    vault = bucket['vault'],
                    path = path,
                    title = title,
                    mtime = int(getmtime(filepath)),
                    score = score,
                ))
    items = [r for r in items if r['score'] > 0] if search != '' else items
    items = sorted(items, key=lambda r: (-r['score'],-r['mtime']))
    data = paginate(request, items, page=page, perpage=50)
    return data
