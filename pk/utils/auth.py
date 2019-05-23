# encoding: utf-8
import httplib2
from apiclient import discovery
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_POST
from oauth2client import client
from pk import log, utils

GAUTH_KEY = 'gauth:{email}'


@require_POST
def user_login(request):
    try:
        user = auth_django(request)
        if user and user.is_active:
            return utils.response_json_success()
        return utils.response_json_error('Invalid username or password.')
    except Exception as err:
        return utils.response_json_error(str(err))


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return utils.response_json_success()
        return utils.response_json_error(form.errors)
    form = PasswordChangeForm(request.user)
    form.fields['old_password'].label = 'Current Password'
    form.fields['new_password1'].label = 'New Password'
    form.fields['new_password2'].label = 'Confirm Password'
    return utils.response_modal(dict(form=form))


def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


def auth_django(request):
    """ Authenticate with Django and return the user. """
    email = request.POST.get('email')
    test = utils.get_object_or_none(User, Q(email=email) | Q(username=email))
    passwd = request.POST.get('password')
    user = authenticate(username=test.username, password=passwd)
    if user and user.is_active:
        login(request, user)
        log.info('Logged in via Django as %s' % user.email)
        return user


def auth_google(request):
    """ Authenticate with Google and return the user.
        https://developers.google.com/identity/sign-in/web/server-side-flow
        https://developers.google.com/gmail/api/auth/web-server
    """
    code = request.POST.get('code')
    credentials = client.credentials_from_clientsecrets_and_code(
        settings.GOOGLE_SECRET, settings.GOOGLE_SCOPES, code)
    credentials.authorize(httplib2.Http())
    user = User.objects.get(email=credentials.id_token['email'])
    if user and user.is_active:
        login(request, user)
        key = GAUTH_KEY.replace('{email}', user.email)
        cache.set(key, credentials.to_json(), 31557600)  # 1yr
        log.info('Logged in via Google as %s' % user.email)
        return user


def get_gauth_service(email, service, version='v1'):
    """ Return gauth credentials for the specified user or None. """
    key = GAUTH_KEY.replace('{email}', email)
    credentials = client.OAuth2Credentials.from_json(cache.get(key))
    httpauth = credentials.authorize(httplib2.Http())
    service = discovery.build(service, version, http=httpauth)
    return service
