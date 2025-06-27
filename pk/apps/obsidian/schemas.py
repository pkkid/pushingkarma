# encoding: utf-8
from datetime import datetime
from ninja import Schema
from typing import List, Optional
from pydantic import Field


class NoteSchema(Schema):
    url: str = Field(..., description='URL for the note resource')
    bucket: str = Field(..., description='Name of bucket this note belongs to')
    vault: str = Field(..., description='Name of vault this note belongs to')
    path: str = Field(..., description='Path to note file in the bucket')
    title: str = Field(..., description='Title of the note')
    icon: Optional[str] = Field(None, description='Icon for this note')
    content: Optional[str] = Field(None, description='Markdown content of the note')
    mtime: datetime = Field(..., description='Datetime note was last modified')
    score: Optional[int] = Field(None, description='Search score for this note')


class StaticSchema(Schema):
    class StaticItemSchema(Schema):
        url: str = Field(..., description='Url of the static item')
        size: int = Field(None, description='File size of the static item in bytes')
        mtime: datetime = Field(None, description='Last modified time of the static item')
        ctime: datetime = Field(None, description='Creation time of the static item')
        ptime: datetime = Field(None, description='Original date of the image, if applicable')
    bucket: str = Field(..., description='Name of bucket for static resources')
    vault: str = Field(..., description='Name of vault for static resources')
    count: int = Field(None, description='Count of static resources in the bucket')
    items: List[StaticItemSchema] = Field(..., description='List of static items')
