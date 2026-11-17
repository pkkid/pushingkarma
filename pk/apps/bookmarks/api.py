# encoding: utf-8
"""
Bookmarks API for the new tab bookmarks bar. Bookmarks are a small tree per user, so
every endpoint returns the complete tree and the client simply replaces its copy.
"""
import html, logging, re, requests
from django.db import transaction
from django.shortcuts import get_object_or_404
from ninja import Body, Path, Query, Router
from ninja.errors import HttpError
from typing import List
from urllib.parse import unquote, urlparse
from pk.utils.ninja import user_auth
from . import schemas
from .models import Bookmark, FOLDER, LINK
log = logging.getLogger(__name__)
router = Router(auth=user_auth)
TITLE_REGEX = re.compile(rb'<title[^>]*>(.*?)</title>', re.IGNORECASE | re.DOTALL)
TITLE_MAXBYTES = 512 * 1024
TITLE_HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0'}


def get_tree(user):
    """ Return the user's bookmarks as a nested list of dicts. """
    nodes = {b.id: dict(id=b.id, kind=b.kind, title=b.title, url=b.url, parent=b.parent_id, children=[])
        for b in Bookmark.objects.filter(user=user)}
    roots = []
    for node in nodes.values():
        siblings = nodes[node['parent']]['children'] if node['parent'] else roots
        siblings.append(node)
    return roots


def get_folder(user, pk):
    """ Return the folder with the specified pk, or None for the bar itself. """
    if pk is None: return None
    folder = Bookmark.objects.filter(user=user, id=pk, kind=FOLDER).first()
    if folder is None:
        raise HttpError(400, 'Parent folder not found.')
    return folder


def move_bookmark(item, parent, index=None):
    """ Move item into the parent folder at index (end of the folder if None). """
    # Make sure we are not moving a folder into itself or a descendant
    ancestor = parent
    while ancestor:
        if ancestor.id == item.id:
            raise HttpError(400, 'Cannot move a folder into itself.')
        ancestor = ancestor.parent
    # Insert the item into its new siblings and renumber them
    siblings = list(Bookmark.objects.filter(user=item.user, parent=parent).exclude(id=item.id))
    index = len(siblings) if index is None else max(0, min(index, len(siblings)))
    siblings.insert(index, item)
    item.parent = parent
    for sortid, sibling in enumerate(siblings):
        sibling.sortid = sortid
    Bookmark.objects.bulk_update(siblings, ['parent', 'sortid'])


@router.get('', response=List[schemas.BookmarkSchema])
def list_bookmarks(request):
    """ List the bookmarks tree for the logged in user. """
    return get_tree(request.user)


@router.get('/title', response=schemas.PageTitleSchema)
def page_title(request, url: str=Query(..., description='Page url to read the title from')):
    """ Return a title for the url. Reads the page <title> tag when the site can be reached,
        otherwise builds one from the url slug, and finally falls back to the domain name.
        The browser can't read other sites directly, so the server looks it up for the editor.
    """
    if not re.match(r'^https?://', url, re.IGNORECASE):
        raise HttpError(400, 'Only http and https urls are supported.')
    return {'title': _fetch_title(url) or _slug_title(url) or _domain_title(url)}


def _fetch_title(url):
    """ Fetch the url and return the contents of its <title> tag, or '' when the site
        can't be reached, returns an error page, or has no title.
    """
    try:
        # Read only the start of the page, the title is near the top
        content = b''
        with requests.get(url, headers=TITLE_HEADERS, timeout=5, stream=True) as response:
            response.raise_for_status()
            for chunk in response.iter_content(16384):
                content += chunk
                if TITLE_REGEX.search(content) or len(content) >= TITLE_MAXBYTES: break
            encoding = response.encoding if 'charset' in response.headers.get('content-type', '') else 'utf-8'
        # Decode and clean up the title whitespace and html entities
        match = TITLE_REGEX.search(content)
        title = match.group(1).decode(encoding or 'utf-8', errors='replace') if match else ''
        return ' '.join(html.unescape(title).split())
    except requests.RequestException as err:
        log.info(f'Unable to read page title from {url}: {err}')
        return ''


def _slug_title(url):
    """ Build a title from the last url path segment that reads like a slug (at least two
        words with letters joined by dashes or underscores), ie: /posts/123/how-to-cook-rice.html
        becomes "How To Cook Rice". Words with digits that look like ids are dropped.
    """
    for segment in reversed(unquote(urlparse(url).path).split('/')):
        words = re.split(r'[-_+\s]+', re.sub(r'\.[a-z]{2,5}$', '', segment, flags=re.IGNORECASE))
        words = [w for w in words if w and not (len(w) >= 6 and re.search(r'\d', w))]
        if sum(bool(re.search(r'[^\W\d]', w)) for w in words) >= 2:
            return ' '.join(w[:1].upper() + w[1:] for w in words)
    return ''


def _domain_title(url):
    """ Return the url domain without www, ie: https://www.example.com/a becomes example.com. """
    return re.sub(r'^www\.', '', urlparse(url).hostname or '')


@router.post('', response=List[schemas.BookmarkSchema])
@transaction.atomic
def create_bookmark(request, data: schemas.BookmarkCreateSchema=Body(...)):
    """ Create a bookmark at the end of the specified folder. """
    if data.kind == LINK and not data.url.strip():
        raise HttpError(400, 'URL is required for links.')
    parent = get_folder(request.user, data.parent)
    item = Bookmark.objects.create(user=request.user, parent=parent, kind=data.kind,
        title=data.title.strip(), url=data.url.strip() if data.kind == LINK else '')
    move_bookmark(item, parent)
    return get_tree(request.user)


@router.patch('/{pk}', response=List[schemas.BookmarkSchema])
@transaction.atomic
def update_bookmark(request,
      pk: int=Path(..., description='Primary key of bookmark to update'),
      data: schemas.BookmarkPatchSchema=Body(...)):
    """ Update the title or url of a bookmark, or move it to the end of another folder. """
    item = get_object_or_404(Bookmark, user=request.user, id=pk)
    fields = data.dict(exclude_unset=True)
    if 'title' in fields: item.title = (fields['title'] or '').strip()
    if 'url' in fields and item.kind == LINK: item.url = (fields['url'] or '').strip()
    item.save()
    if 'parent' in fields and fields['parent'] != item.parent_id:
        move_bookmark(item, get_folder(request.user, fields['parent']))
    return get_tree(request.user)


@router.delete('/{pk}', response=List[schemas.BookmarkSchema])
def delete_bookmark(request,
      pk: int=Path(..., description='Primary key of bookmark to delete')):
    """ Delete a bookmark (and everything inside it if it is a folder). """
    get_object_or_404(Bookmark, user=request.user, id=pk).delete()
    return get_tree(request.user)


@router.post('/{pk}/move', response=List[schemas.BookmarkSchema])
@transaction.atomic
def move(request,
      pk: int=Path(..., description='Primary key of bookmark to move'),
      data: schemas.BookmarkMoveSchema=Body(...)):
    """ Move a bookmark to the specified folder and position. """
    item = get_object_or_404(Bookmark, user=request.user, id=pk)
    move_bookmark(item, get_folder(request.user, data.parent), data.index)
    return get_tree(request.user)
