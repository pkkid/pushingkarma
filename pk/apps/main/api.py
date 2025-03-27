# encoding: utf-8
import logging
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from ninja import Router
from ninja.errors import HttpError
from pk import utils
from .schemas import GlobalVarsSchema, UserSchema, LoginSchema
log = logging.getLogger(__name__)
router = Router()


@router.get('/global_vars', response=GlobalVarsSchema)
def get_global_vars(request):
    """ Return global variables. """
    result = dict(**settings.GLOBALVARS)
    result['user'] = UserSchema.from_user(request.user)
    return result


@router.post('/login', response=UserSchema)
def login(request, data:LoginSchema):
    """ Allows logging in to the django application.
        • email (str): Email of the account to log into.
        • password (str): Password of the account to log into.
    """
    try:
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


@router.post('/logout', response=dict)
def logout(request, *args, **kwargs):
    """ Logs the current user out. """
    django_logout(request)
    return {'status': 'Successfully logged out.'}
