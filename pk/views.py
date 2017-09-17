#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from pk import utils
from pk.models import AccountSerializer
from rest_framework import status, viewsets
from rest_framework.decorators import detail_route
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


class AccountViewSet(viewsets.ViewSet):
    queryset = User.objects.filter(pk=-1)
    serializer_class = AccountSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)

    def list(self, request, *args, **kwargs):
        serializer = AccountSerializer(self.request.user, context={'request':request})
        return Response(serializer.data)

    @detail_route(methods=['post'])
    def login(self, request, *args, **kwargs):
        try:
            email = request.POST.get('email')
            test = utils.get_object_or_none(User, Q(email=email) | Q(username=email))
            passwd = request.POST.get('password')
            user = authenticate(username=test.username, password=passwd)
            if user and user.is_active:
                login(request, user)
                serializer = AccountSerializer(user, context={'request':request})
                return Response(serializer.data)
        except Exception as err:
            print(err)
        return Response(status=status.HTTP_403_FORBIDDEN)

    @detail_route(methods=['post'])
    def logout(self, request, *args, **kwargs):
        logout(request)
        return Response({'status': 'Successfully logged out.'})
