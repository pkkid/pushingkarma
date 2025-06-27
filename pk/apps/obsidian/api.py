# encoding: utf-8
import json, glob, logging, re
from django.conf import settings
from django.views.decorators.cache import cache_page
from ninja import Path, Query, Router
from ninja.decorators import decorate_view
from ninja.errors import HttpError
from os import listdir
from os.path import basename, exists, getctime, getmtime, join
from os.path import getsize, isdir, isfile, normpath
from pk.utils.django import reverse
from pk.utils.ninja import PageSchema, paginate
from .schemas import NoteSchema, StaticSchema
log = logging.getLogger(__name__)
router = Router()


@router.get('/notes/{bucket}/{path:path}', response=NoteSchema, exclude_unset=True, url_name='note')
def get_note(request,
      bucket: str=Path(None, description='Name of Obsidian bucket in settings.py'),
      path: str=Path(None, description='Path of note in the bucket')):
    """ Returns a single note from the obsian vault. The path is relative to the
        vault bucket. The bucketname is the name of the group in settings.py.
    """
    if bucket not in settings.OBSIDIAN_BUCKETS:
        raise HttpError(404, 'Unknown bucket name.')
    bucket, bucketname = settings.OBSIDIAN_BUCKETS[bucket], bucket
    check_permission = bucket.get('check_permission', lambda user: True)
    if check_permission(request.user):
        icons = _get_bucket_icons(bucket)
        filepath = join(bucket['path'], path)
        if not exists(filepath):
            raise HttpError(404, 'Unknown note path.')
        with open(filepath, 'r', encoding='utf-8') as handle:
            content = handle.read()
        return dict(
            url = reverse('api:note', bucket=bucketname, path=path),
            bucket = bucketname,
            vault = bucket['vault'],
            path = path,
            title = basename(filepath)[:-3],
            icon = icons.get(filepath),
            content = content,
            mtime = int(getmtime(filepath))
        )
    raise HttpError(403, 'Permission denied.')


@router.get('/notes', response=PageSchema(NoteSchema), exclude_unset=True)
@decorate_view(cache_page(0 if settings.DEBUG else 300))
def list_notes(request,
      search: str=Query('', description='Search term to filter notes'),
      page: int=Query(1, description='Page number of results to return')):
    """ Lists obsidian notes in the defined groups from settings. When searching,
        each word in the search string is counted in the content and title to give
        a score for sorting the results. The results are sorted by count and mtime,
        and returned as a list of dictionaries.
    """
    items = []
    icons = _get_all_icons()
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
                score = sum(filepath.lower().count(word) for word in words) * 100
                score += sum(content.lower().count(word) for word in words)
                items.append(dict(
                    url = reverse('api:note', bucket=bucketname, path=path),
                    bucket = bucketname,
                    vault = bucket['vault'],
                    path = path,
                    title = title,
                    icon = icons.get(bucketname, {}).get(filepath),
                    mtime = int(getmtime(filepath)),
                    score = score,
                ))
    items = [r for r in items if r['score'] > 0] if search != '' else items
    items = sorted(items, key=lambda r: (-r['score'],r['title']))
    data = paginate(request, items, page=page, perpage=50)
    return data


@router.get('/static/{bucket}/{path:path}', response=StaticSchema, exclude_unset=True)
@decorate_view(cache_page(0 if settings.DEBUG else 300))
def list_static(request,
      bucket: str=Path(..., description='Name of Obsidian bucket in settings.py'),
      path: str=Path(..., description='Path of static resources in the bucket'),
      filetype: str=Query(None, description='Filetype to filter by. ex: png or jpg'),
      sortby: str=Query('ctime', description='Sort by field (ctime, mtime, name)'),
      sort: str=Query('desc', description='Sort order (desc, asc)')):
    """ Lists static resources for the specified path. Not recursive. """
    if bucket not in settings.OBSIDIAN_BUCKETS:
        raise HttpError(404, 'Unknown bucket name.')
    bucket, bucketname = settings.OBSIDIAN_BUCKETS[bucket], bucket
    check_permission = bucket.get('check_permission', lambda user: True)
    staticroot = f'{bucket['path']}/_static'
    fullpath = normpath(join(staticroot, path))
    # Check permissions and path
    if not check_permission(request.user):
        log.warning(f'check_permission failed for user {request.user}')
        raise HttpError(403, 'Permission denied.')
    if not fullpath.startswith(staticroot):
        log.warning(f'fullpath does not start with staticroot {fullpath}')
        raise HttpError(403, 'Permission denied.')
    if not exists(fullpath) or not isdir(fullpath):
        log.warning(f'path doesnt exist or is not a directory {fullpath}')
        raise HttpError(403, 'Permission denied.')
    # List files in the requested path
    items = []
    ext = f'.{filetype.lower()}' if filetype else ''
    for entry in listdir(fullpath):
        entrypath = join(fullpath, entry)
        if not isfile(entrypath): continue
        if ext and not entry.lower().endswith(ext): continue
        items.append({
            'name': entry,
            'size': getsize(entrypath),
            'mtime': int(getmtime(entrypath)),
            'ctime': int(getctime(entrypath)),
        })
    # Sort items and return the response
    reverse = sort == 'desc'
    return dict(
        bucket = bucketname,
        vault = bucket['vault'],
        count = len(items),
        items = sorted(items, key=lambda r:r[sortby], reverse=reverse),
    )


def _get_all_icons():
    """ Returns a dict of {path: icon} for all notes in all buckets. """
    icons = {}
    for bucketname, bucket in settings.OBSIDIAN_BUCKETS.items():
        icons[bucketname] = _get_bucket_icons(bucket)
    return icons


def _get_bucket_icons(bucket):
    """ Returns a dict of {path: icon} for all notes in the bucket. """
    icons = {}
    datapath = f'{bucket['root']}/.obsidian/plugins/obsidian-icon-folder/data.json'
    with open(datapath, 'r', encoding='utf-8') as handle:
        data = json.load(handle)
    for path, icon in data.items():
        filepath = f'{bucket['root']}/{path}'
        if filepath.startswith(bucket['path']):
            icons[filepath] = re.sub(r'([A-Z])', r'-\1', icon).lower().strip('-')
    return icons
