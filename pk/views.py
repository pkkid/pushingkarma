#!/usr/bin/env python
# encoding: utf-8
import httplib2
from apiclient import discovery
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from oauth2client import client
from pk import log, utils
from rest_framework import status, viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import AccountSerializer


class AccountViewSet(viewsets.ViewSet):
    queryset = User.objects.filter(pk=-1)
    serializer_class = AccountSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)

    def list(self, request, *args, **kwargs):
        serializer = AccountSerializer(self.request.user, context={'request':request})
        return Response(serializer.data)

    @list_route(methods=['post'])
    def login(self, request, *args, **kwargs):
        try:
            authcode = request.POST.get('code')
            if authcode:
                # Google Login
                # https://developers.google.com/identity/sign-in/web/server-side-flow
                # https://developers.google.com/gmail/api/auth/web-server#exchange_the_authorization_code_for_an_access_token
                credentials = client.credentials_from_clientsecrets_and_code(
                    settings.GOOGLE_CLIENT_SECRET, settings.GOOGLE_SCOPES, authcode)
                credentials.authorize(httplib2.Http())
                user = User.objects.get(email=credentials.id_token['email'])
            else:
                # Regular Django login
                email = request.POST.get('email')
                test = utils.get_object_or_none(User, Q(email=email) | Q(username=email))
                passwd = request.POST.get('password')
                user = authenticate(username=test.username, password=passwd)
            # Login
            if user and user.is_active:
                login(request, user)
                serializer = AccountSerializer(user, context={'request':request})
                log.info('Logged in as %s' % serializer.data)
                return Response(serializer.data)
        except Exception as err:
            log.error(err, exc_info=1)
        return Response(status=status.HTTP_403_FORBIDDEN)

    @list_route(methods=['post'])
    def logout(self, request, *args, **kwargs):
        logout(request)
        return Response({'status': 'Successfully logged out.'})
