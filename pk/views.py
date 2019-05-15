#!/usr/bin/env python
# encoding: utf-8
from django.contrib.auth import logout
from django.contrib.auth.models import User
from rest_framework import status, viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from pk import log
from pk import utils
from pk.utils.auth import auth_django, auth_google
from .models import AccountSerializer


def index(request, tmpl='page.html'):
    return utils.response(request, tmpl, {})


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
            code = request.POST.get('code')
            user = auth_google(request) if code else auth_django(request)
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
