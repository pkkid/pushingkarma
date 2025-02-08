# encoding: utf-8
import binascii, logging, os
from pk import utils
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .api import AccountSerializer
log = logging.getLogger(__name__)


@api_view(['get'])
def globalvars(request, *args, **kwargs):
    """ Return global variables. """
    result = dict(**settings.GLOBALVARS)
    result['user'] = AccountSerializer(request.user, context={'request':request}).data
    return Response(result)


@api_view(['post'])
def generate_token(request, *args, **kwargs):
    """ Generates a new token for the logged in user. """
    if request.user.is_active:
        if token := utils.get_object_or_none(Token, user=request.user.id):
            token.delete()
        key = binascii.hexlify(os.urandom(10)).decode()
        Token.objects.get_or_create(user=request.user, key=key)
    serializer = AccountSerializer(request.user, context={'request':request})
    return Response(serializer.data)


@api_view(['post'])
@permission_classes([AllowAny])
def login(request, *args, **kwargs):
    """ Allows logging in to the django application.
        email: Email of the account to log into.
        password: Password of the account to log into.
    """
    try:
        email = request.data.get('email')
        password = request.data.get('password')
        user = utils.get_object_or_none(User, email=email)
        if user is not None:
            user = authenticate(username=user.username, password=password)
            if user and user.is_active:
                django_login(request, user)
                log.info('Logged in as %s', user.email)
                serializer = AccountSerializer(user, context={'request':request})
                return Response(serializer.data)
            log.info('Unknown email or password: %s', email)
    except Exception as err:
        log.error(err, exc_info=1)
    return Response({'status': 'Unknown email or password.'}, status=status.HTTP_403_FORBIDDEN)


@api_view(['post'])
def logout(request, *args, **kwargs):
    """ Logs the current user out. """
    django_logout(request)
    return Response({'status': 'Successfully logged out.'})


@api_view(['get'])
@permission_classes([AllowAny])
def user(request, *args, **kwargs):
    """ Returns details of the currently logged in user. """
    serializer = AccountSerializer(request.user, context={'request':request})
    return Response(serializer.data)
