# encoding: utf-8
from django.contrib.auth import logout
from django.contrib.auth.models import User
from pk import log, utils
from pk.utils import auth
from rest_framework import status, viewsets
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import list_route
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


class AccountViewSet(viewsets.ViewSet):
    queryset = User.objects.filter(pk=-1)
    serializer_class = AccountSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [AllowAny]

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)

    def list(self, request, *args, **kwargs):
        serializer = AccountSerializer(self.request.user, context={'request':request})
        return Response(serializer.data)

    @list_route(methods=['post'])
    def gentoken(self, request, *args, **kwargs):
        if request.user.is_active:
            token = utils.get_object_or_none(Token, user=request.user.id)
            if token: token.delete()
            Token.objects.get_or_create(user=request.user)
        serializer = AccountSerializer(request.user, context={'request':request})
        return Response(serializer.data)

    @list_route(methods=['post'])
    def login(self, request, *args, **kwargs):
        try:
            email = request.data.get('email')
            passwd = request.data.get('password')
            code = request.data.get('code')
            user = (auth.auth_google(request, code) if code
                else auth.auth_django(request, email, passwd))
            if user and user.is_active:
                serializer = AccountSerializer(user, context={'request':request})
                return Response(serializer.data)
        except Exception as err:
            log.error(err, exc_info=1)
        return Response(status=status.HTTP_403_FORBIDDEN)

    @list_route(methods=['post'])
    def logout(self, request, *args, **kwargs):
        logout(request)
        return Response({'status': 'Successfully logged out.'})
