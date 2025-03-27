# encoding: utf-8
from django.contrib.auth.models import User
from ninja import ModelSchema, Schema
from typing import Optional
from django.forms.models import model_to_dict


class UserSchema(ModelSchema):
    name: Optional[str] = None
    # auth_token: str | None

    class Config:
        model = User
        model_fields = ['id', 'email', 'date_joined', 'last_login']

    @staticmethod
    def from_user(user):
        """ Populate schema from a user object. """
        userdict = model_to_dict(user)
        userdict['name'] = user.get_full_name() if user.is_active else 'Guest'
        return UserSchema(**userdict).dict()


        schema = UserSchema.from_orm(user)  # Automatically map model fields
        # token = utils.get_object_or_none(Token, user=user.id or -1)
        # schema.auth_token = token.key if token else None  # Add the extra field
        schema.name = user.get_full_name() if user.is_active else 'Guest'
        return schema


class LoginSchema(Schema):
    email: str
    password: str
