# encoding: utf-8
import graphene
from django.contrib.auth import logout
from django.contrib.auth.models import User
from graphene_django.types import DjangoObjectType, ObjectType
from graphql.error import GraphQLError
from pk.apps.notes.schema import NoteQuery, SaveNote
from pk.utils import auth
from pk import log


class UserType(DjangoObjectType):
    class Meta:
        model = User
        only_fields = ['id', 'email', 'first_name', 'last_name', 'date_joined', 'last_login']


class UserQuery(ObjectType):
    user = graphene.Field(UserType, id=graphene.Int())
    users = graphene.List(UserType)
    current_user = graphene.Field(UserType)
    login = graphene.Field(UserType, email=graphene.String(),
        password=graphene.String(), code=graphene.String())
    logout = graphene.Field(UserType)

    def resolve_user(parent, info, **kwargs):
        userid = kwargs.get('id')
        if userid is not None:
            return User.objects.get(pk=id)
        return None

    def resolve_users(parent, info, **kwargs):
        return User.objects.all()

    def resolve_current_user(parent, info):
        if info.context.user.is_active:
            return info.context.user
        return None
    
    def resolve_login(parent, info, email=None, password=None, code=None, **kwargs):
        try:
            user = (auth.auth_google(info.context, code) if code
                else auth.auth_django(info.context, email, password))
            if user and user.is_active:
                return user
        except Exception as err:
            log.error(err, exc_info=1)
        raise GraphQLError('Unknown username of password.')
    
    def resolve_logout(self, info):
        logout(info.context)
        return None


# Setup the global Query object. Basically this inherits everything
# we want to make available to the graphql query endpoint.
class Query(UserQuery, NoteQuery, ObjectType):
    pass

class Mutations(graphene.ObjectType):  # noqa
    save_note = SaveNote.Field()

schema = graphene.Schema(query=Query, mutation=Mutations)  # noqa
