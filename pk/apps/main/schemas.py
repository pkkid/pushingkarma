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
    apikey: Optional[str] = Field(None, description='Api key for this user (apikey url argument or X-Apikey header)')

    @staticmethod
    def resolve_apikey(obj):
        apikey = getattr(obj, 'apikey', None)
        return apikey.key if apikey else None


class LoginSchema(Schema):
    email: str = Field(..., description='User email address')
    password: str = Field(..., description='User password')


class GlobalVarsSchema(Schema):
    DEBUG: bool = Field(..., description='True if site running in debug mode')
    DOMAIN: str = Field(..., description='Domain the Django app is configured for')
    user: Optional[UserSchema] = Field(None, description='Currently logged in user')
    apikey_auth: bool = Field(False, description='True if the user was authenticated with an api key')


class AiPromptQuestionSchema(Schema):
    prompt: str = Field(..., description='Prompt sent to the AI provider')


class AiPromptResponseSchema(Schema):
    response: str = Field(..., description='Text response from the AI provider')


class BackgroundSchema(Schema):
    name: str = Field(..., description='Filename of the background image')
    url: str = Field(..., description='Url of the background image')
    description: Optional[str] = Field(None, description='Where and when the image was taken')
