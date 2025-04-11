# encoding: utf-8
from datetime import datetime
from ninja import Schema
from typing import Optional
from pydantic import Field


class UserSchema(Schema):
    id: Optional[int] = Field(..., description='Internal user id')
    first_name: str = Field(..., description='User first name')
    last_name: str = Field(..., description='User last name')
    email: Optional[str] = Field(..., description='User email address')
    date_joined: Optional[datetime] = Field(..., description='Datetime user joined the system')
    last_login: Optional[datetime] = Field(..., description='Datetime user last logged in')


class LoginSchema(Schema):
    email: str = Field(..., description='User email address')
    password: str = Field(..., description='User password')


class GlobalVarsSchema(Schema):
    DEBUG: bool = Field(..., description='True if site running in debug mode')
    user: Optional[UserSchema] = Field(None, description='Currently logged in user')
