# encoding: utf-8
from datetime import datetime
from ninja import Schema
from typing import Optional
from pydantic import Field


class NoteSchema(Schema):
    url: str = Field(..., description='URL for the note resource')
    bucket: str = Field(..., description='Name of bucket this note belongs to')
    vault: str = Field(..., description='Name of vault this note belongs to')
    path: str = Field(..., description='Path to note file in the bucket')
    title: str = Field(..., description='Title of the note')
    content: Optional[str] = Field(None, description='Markdown content of the note')
    mtime: datetime = Field(..., description='Datetime note was last modified')
    score: Optional[int] = Field(None, description='Search score for this note')
