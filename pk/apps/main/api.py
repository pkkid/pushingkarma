# encoding: utf-8
from pk import utils
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.serializers import SerializerMethodField, ModelSerializer


class AccountSerializer(ModelSerializer):
    name = SerializerMethodField()
    auth_token = SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'date_joined', 'last_login', 'auth_token')
    
    def get_name(self, obj):
        return obj.get_full_name() if obj.is_active else 'Guest'

    def get_auth_token(self, obj):
        token = utils.get_object_or_none(Token, user=obj.id or -1)
        return token.key if token else None
