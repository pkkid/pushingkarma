# encoding: utf-8
from django.contrib.auth.models import User
from rest_framework import serializers


class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id','email','first_name','last_name','date_joined','last_login')
