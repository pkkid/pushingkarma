#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from pk.models import Note, Page
from pk import serializers, utils
from rest_framework import status, viewsets
from rest_framework.decorators import detail_route
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response


class AccountViewSet(viewsets.ViewSet):
    queryset = User.objects.filter(pk=-1)
    serializer_class = serializers.AccountSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)

    def list(self, request, *args, **kwargs):
        serializer = serializers.AccountSerializer(self.request.user, context={'request':request})
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
                serializer = serializers.AccountSerializer(user, context={'request':request})
                return Response(serializer.data)
        except Exception as err:
            print(err)
        return Response(status=status.HTTP_403_FORBIDDEN)

    @detail_route(methods=['post'])
    def logout(self, request, *args, **kwargs):
        logout(request)
        return Response({'status': 'Successfully logged out.'})


class NotesViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.order_by('-created')
    serializer_class = serializers.NoteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    list_fields = ['id','url','title','tags','created','modified']

    def list(self, request, *args, **kwargs):
        notes = Note.objects.order_by('-created')
        serializer = serializers.NoteSerializer(notes, context={'request':request},
            many=True, fields=self.list_fields)
        return Response(serializer.data)


class PagesViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.order_by('-created')
    serializer_class = serializers.PageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    list_fields = ['id','url','slug','created','modified']

    def list(self, request, *args, **kwargs):
        queryset = Page.objects.order_by('-created')
        serializer = serializers.PageSerializer(queryset, context={'request':request},
            many=True, fields=self.list_fields)
        return Response(serializer.data)
