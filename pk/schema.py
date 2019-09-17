# encoding: utf-8
import graphene
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db.models import Q
from pk import log, utils
from pk.apps.notes.schema import NoteQuery
from graphene_django.types import DjangoObjectType, ObjectType
from graphql.error import GraphQLError


class UserType(DjangoObjectType):
    class Meta:
        model = User
        only_fields = ['id', 'email']


class UserQuery(ObjectType):
    user = graphene.Field(UserType, id=graphene.Int())
    users = graphene.List(UserType)
    
    current_user = graphene.Field(UserType)
    login = graphene.Field(UserType, email=graphene.String(), password=graphene.String())
    logout = None

    def resolve_user(self, info, **kwargs):
        userid = kwargs.get('id')
        if userid is not None:
            return User.objects.get(pk=id)
        return None

    def resolve_users(self, info, **kwargs):
        return User.objects.all()

    def resolve_current_user(self, info):
        if info.context.user.is_active:
            return info.context.user
        return None
    
    def resolve_login(self, info, email=None, password=None, code=None, **kwargs):
        try:
            user = _auth_django(info.context, email, password)
            if user and user.is_active:
                return user
        except Exception as err:
            log.error(err, exc_info=1)
        raise GraphQLError('Unknown username of password.')
        # ---------
        # try:
        #     code = request.POST.get('code')
        #     user = auth_google(request) if code else auth_django(request)
        #     if user and user.is_active:
        #         serializer = AccountSerializer(user, context={'request':request})
        #         return Response(serializer.data)
        # except Exception as err:
        #     log.error(err, exc_info=1)
        # return Response(status=status.HTTP_403_FORBIDDEN)


def _auth_django(request, email, password):
    log.info(email)
    test = utils.get_object_or_none(User, email=email)
    user = authenticate(username=test.username, password=password)
    if user and user.is_active:
        login(request, user)
        log.info('Logged in via Django as %s', user.email)
        return user


# Setup the global Query object. Basically this inherits everything
# we want to make available to the graphql query endpoint.
class Query(UserQuery, NoteQuery, ObjectType):
    pass
schema = graphene.Schema(query=Query)  # noqa
