# encoding: utf-8
import httplib2
from apiclient import discovery
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect
from oauth2client import client

from pk import log, utils

GAUTH_KEY = 'gauth:{email}'


def auth_django(request, email, password):
    """ Authenticate with Django and return the user. """
    test = utils.get_object_or_none(User, Q(email=email) | Q(username=email))
    if test:
        user = authenticate(username=test.username, password=password)
        if user and user.is_active:
            login(request, user)
            log.info('Logged in via Django as %s', user.email)
            return user


def auth_google(request, code):
    """ Authenticate with Google and return the user.
        https://developers.google.com/identity/sign-in/web/server-side-flow
        https://developers.google.com/gmail/api/auth/web-server
    """
    credentials = client.credentials_from_clientsecrets_and_code(
        settings.GOOGLE_SECRET, settings.GOOGLE_SCOPES, code)
    credentials.authorize(httplib2.Http())
    user = User.objects.get(email=credentials.id_token['email'])
    if user and user.is_active:
        login(request, user)
        key = GAUTH_KEY.replace('{email}', user.email)
        cache.set(key, credentials.to_json(), 31557600)  # 1yr
        log.info('Logged in via Google as %s', user.email)
        return user


def get_gauth_service(email, service, version='v1'):
    """ Return gauth credentials for the specified user or None. """
    key = GAUTH_KEY.replace('{email}', email)
    credentials = client.OAuth2Credentials.from_json(cache.get(key))
    httpauth = credentials.authorize(httplib2.Http())
    service = discovery.build(service, version, http=httpauth)
    return service


@require_POST
def django_login(request):
    """ Login function for use with Django urls. """
    try:
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = auth_django(request, email, password)
        if user and user.is_active:
            return utils.response_json_success()
        return utils.response_json_error('Invalid username or password.')
    except Exception as err:
        return utils.response_json_error(str(err))


@require_POST
def django_change_password(request):
    """ Change password handler. Requires you to pass the following
        POST args: old_password, new_password1, new_password1
    """
    form = PasswordChangeForm(request.user, request.POST)
    if form.is_valid():
        form.save()
        return utils.response_json_success()
    return utils.response_json_error(form.errors)


def django_logout(request):
    """ Logout function for use with Django urls. """
    logout(request)
    return HttpResponseRedirect('/')
