# encoding: utf-8
from datetime import datetime
from ninja import Schema
from typing import Optional
from django.forms.models import model_to_dict


class UserSchema(Schema):
    id: Optional[int]
    name: str
    email: Optional[str]
    date_joined: Optional[datetime]
    last_login: Optional[datetime]

    @staticmethod
    def from_user(user):
        """ Populate schema from a user object. """
        userdict = model_to_dict(user)
        userdict['name'] = user.get_full_name() if user.is_active else 'Guest'
        return UserSchema(**userdict)


class LoginSchema(Schema):
    email: str
    password: str
