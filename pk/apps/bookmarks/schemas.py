# encoding: utf-8
from ninja import Schema
from typing import List, Literal, Optional
from pydantic import Field


class BookmarkSchema(Schema):
    id: int = Field(..., description='Internal bookmark id')
    kind: str = Field(..., description='Bookmark kind: link, folder or separator')
    title: str = Field('', description='Display title of this bookmark')
    url: str = Field('', description='URL for link bookmarks')
    children: List['BookmarkSchema'] = Field([], description='Child bookmarks for folders')


class BookmarkCreateSchema(Schema):
    kind: Literal['link', 'folder', 'separator'] = Field('link', description='Bookmark kind')
    title: str = Field('', description='Display title of this bookmark')
    url: str = Field('', description='URL for link bookmarks')
    parent: Optional[int] = Field(None, description='Parent folder id (null for the bar itself)')


class BookmarkPatchSchema(Schema):
    title: Optional[str] = Field(None, description='Display title of this bookmark')
    url: Optional[str] = Field(None, description='URL for link bookmarks')
    parent: Optional[int] = Field(None, description='Parent folder id; moves the bookmark to the end of that folder')


class BookmarkMoveSchema(Schema):
    parent: Optional[int] = Field(None, description='Parent folder id (null for the bar itself)')
    index: int = Field(..., description='Position within the parent folder')


BookmarkSchema.model_rebuild()


class PageTitleSchema(Schema):
    title: str = Field('', description='Title of the page, empty if it could not be read')
