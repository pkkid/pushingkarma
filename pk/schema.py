# encoding: utf-8
import graphene
from django.contrib.auth.models import User
from pk.apps.notes.schema import NoteQuery
from graphene_django.types import DjangoObjectType, ObjectType


class UserType(DjangoObjectType):
    class Meta:
        model = User
        only_fields = ['id', 'email']


class UserQuery(ObjectType):
    user = graphene.Field(UserType, id=graphene.Int())
    users = graphene.List(UserType)

    def resolve_user(self, info, **kwargs):
        userid = kwargs.get('id')
        if userid is not None:
            return User.objects.get(pk=id)
        return None

    def resolve_users(self, info, **kwargs):
        return User.objects.all()


class Query(UserQuery, NoteQuery, ObjectType):
    pass


schema = graphene.Schema(query=Query)
