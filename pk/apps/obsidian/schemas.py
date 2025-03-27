# encoding: utf-8
from datetime import datetime
from ninja import Schema
from typing import Optional


class NoteSchema(Schema):
    bucket: str
    vault: str
    path: str
    title: str
    content: Optional[str] = None
    mtime: datetime
    score: Optional[int] = None
