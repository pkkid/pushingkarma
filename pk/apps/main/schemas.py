# encoding: utf-8
from datetime import datetime
from ninja import Schema
from typing import Optional


class UserSchema(Schema):
    id: Optional[int]
    first_name: str
    last_name: str
    email: Optional[str]
    date_joined: Optional[datetime]
    last_login: Optional[datetime]


class LoginSchema(Schema):
    email: str
    password: str


class GlobalVarsSchema(Schema):
    DEBUG: bool
    user: UserSchema
