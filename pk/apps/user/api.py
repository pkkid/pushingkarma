# encoding: utf-8
from pk import log, utils
from pk.apps.user.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.serializers import SerializerMethodField, ModelSerializer


class AccountSerializer(ModelSerializer):
    name = SerializerMethodField()
    auth_token = SerializerMethodField()
    google_email = SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'date_joined',
            'last_login', 'google_email', 'auth_token')
    
    def get_name(self, obj):
        return obj.get_full_name() if obj.is_active else ''

    def get_auth_token(self, obj):
        token = utils.get_object_or_none(Token, user=obj.id or -1)
        return token.key if token else None
    
    def get_google_email(self, obj):
        try:
            creds, httpauth = obj.google_auth()
            return creds.id_token['email']
        except Exception:
            return ''


@api_view(['get'])
@permission_classes([AllowAny])
def user(request, *args, **kwargs):
    """ Returns details of the currently logged in user. """
    serializer = AccountSerializer(request.user, context={'request':request})
    return Response(serializer.data)


@api_view(['post'])
@permission_classes([AllowAny])
def login(request, *args, **kwargs):
    """ Allows logging in with various authentication schemes.
        You must call this resource using a POST request.
        * email/password - Login with a regular Django account.
        * google_code - Login via Google (email must match django account).
    """
    try:
        email = request.data.get('email')
        password = request.data.get('password')
        google_code = request.data.get('google_code')
        if email and password:
            user = User.auth_django(request, email, password)
        elif google_code:
            user = User.auth_google(request, google_code)
        if user and user.is_active:
            serializer = AccountSerializer(user, context={'request':request})
            return Response(serializer.data)
        log.info('Unknown email or password: %s', email)
    except Exception as err:
        log.error(err, exc_info=1)
    return Response({'status': 'Unknown email or password.'}, status=status.HTTP_403_FORBIDDEN)


@api_view(['post'])
def generate_token(request, *args, **kwargs):
    """ Generates a new token for the logged in user. """
    if request.user.is_active:
        token = utils.get_object_or_none(Token, user=request.user.id)
        if token: token.delete()
        Token.objects.get_or_create(user=request.user)
    serializer = AccountSerializer(request.user, context={'request':request})
    return Response(serializer.data)

@api_view(['post'])
def disconnect(request, *args, **kwargs):
    """ Disconnect the specified account """
    provider = request.data.get('provider')
    request.user.disconnect(provider)
    serializer = AccountSerializer(request.user, context={'request':request})
    return Response(serializer.data)


@api_view(['post'])
def logout(request, *args, **kwargs):
    """ Logs the current user out. """
    User.logout(request)
    return Response({'status': 'Successfully logged out.'})
