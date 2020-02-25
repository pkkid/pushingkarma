# encoding: utf-8
from django.contrib.auth import logout as django_logout
from django.contrib.auth.models import User
from pk import log, utils
from pk.utils import auth
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.serializers import SerializerMethodField, ModelSerializer


class AccountSerializer(ModelSerializer):
    auth_token = SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name',
            'auth_token', 'date_joined', 'last_login')
    
    def get_auth_token(self, obj):
        token = utils.get_object_or_none(Token, user=obj.id or -1)
        return token.key if token else None


@api_view(['get'])
@permission_classes([AllowAny])
def user(request, *args, **kwargs):
    """ Returns details of the currently logged in user. """
    serializer = AccountSerializer(request.user, context={'request':request})
    return Response(serializer.data)


@api_view(['post'])
@permission_classes([AllowAny])
def login(request, *args, **kwargs):
    """ Allows logging in with `user` & `password` or by passing a `code` to authenticate
        using the Google Auth Service. You must call this resource using a POST request.
    """
    try:
        email = request.data.get('email')
        passwd = request.data.get('password')
        code = request.data.get('code')
        user = (auth.auth_google(request, code) if code
            else auth.auth_django(request, email, passwd))
        if user and user.is_active:
            serializer = AccountSerializer(user, context={'request':request})
            return Response(serializer.data)
        log.info('Unknown email or password: %s', email)
    except Exception as err:
        log.error(err, exc_info=1)
    return Response({'status': 'Unknown email or password.'},
        status=status.HTTP_403_FORBIDDEN)


@api_view(['post'])
def gen_token(request, *args, **kwargs):
    """ Generates a new token for the logged in user. """
    if request.user.is_active:
        token = utils.get_object_or_none(Token, user=request.user.id)
        if token: token.delete()
        Token.objects.get_or_create(user=request.user)
    serializer = AccountSerializer(request.user, context={'request':request})
    return Response(serializer.data)


@api_view(['post'])
def logout(request, *args, **kwargs):
    """ Logs the current user out. """
    django_logout(request)
    return Response({'status': 'Successfully logged out.'})
