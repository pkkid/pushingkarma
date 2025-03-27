# encoding: utf-8
import logging
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from ninja import Router
from ninja.errors import HttpError
from pk import utils
from .schemas import UserSchema, LoginSchema
log = logging.getLogger(__name__)
router = Router()


@router.get('/global_vars', response=dict)
def get_global_vars(request):
    """ Return global variables. """
    result = dict(**settings.GLOBALVARS)
    result['user'] = 'Guest'
    return result


@router.post('/login', response=dict)
def login(request, data:LoginSchema):
    """ Allows logging in to the django application.
        • email: Email of the account to log into.
        • password: Password of the account to log into.
    """
    try:
        # email = request.data.get('email')
        # password = request.data.get('password')
        user = utils.get_object_or_none(User, email=data.email)
        if user is not None:
            user = authenticate(username=user.username, password=data.password)
            if user and user.is_active:
                django_login(request, user)
                log.info('Logged in as %s', user.email)
                return UserSchema.from_user(user)
            log.info(f'Unknown email or password: {data.email}')
    except Exception as err:
        log.error(err, exc_info=1)
    return HttpError(403, 'Unknown email or password.')


# ---------------------------------------------
# # encoding: utf-8
# from pk import utils
# from django.contrib.auth.models import User
# from rest_framework.authtoken.models import Token
# from rest_framework.serializers import SerializerMethodField, ModelSerializer


# class AccountSerializer(ModelSerializer):
#     name = SerializerMethodField()
#     auth_token = SerializerMethodField()

#     class Meta:
#         model = User
#         fields = ('id', 'name', 'email', 'date_joined', 'last_login', 'auth_token')
    
#     def get_name(self, obj):
#         return obj.get_full_name() if obj.is_active else 'Guest'

#     def get_auth_token(self, obj):
#         token = utils.get_object_or_none(Token, user=obj.id or -1)
#         return token.key if token else None
