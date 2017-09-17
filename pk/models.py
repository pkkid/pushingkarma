#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from django.contrib.auth.models import User
from rest_framework import serializers


class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username','email','date_joined')
