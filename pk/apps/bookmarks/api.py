# encoding: utf-8
"""
Bookmarks API for the new tab bookmarks bar. Bookmarks are a small tree per user, so
every endpoint returns the complete tree and the client simply replaces its copy.
"""
import logging
from django.db import transaction
from django.shortcuts import get_object_or_404
from ninja import Body, Path, Router
from ninja.errors import HttpError
from ninja.security import django_auth
from typing import List
from . import schemas
from .models import Bookmark, FOLDER, LINK
log = logging.getLogger(__name__)
router = Router(auth=django_auth)


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
