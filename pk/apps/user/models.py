# encoding: utf-8
import httplib2
from apiclient import discovery
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AbstractUser
from django.db import models
from oauth2client import client
from pk import log, utils


class User(AbstractUser):
    google_email = models.EmailField(blank=True, unique=True)   # Last connected Google email address
    google_creds = models.TextField(blank=True)                 # Current Google credentials

    class Meta:
        db_table = 'auth_user'

    def google_auth(self):
        if self.google_creds:
            creds = client.OAuth2Credentials.from_json(self.google_creds)
            if creds and creds.access_token_expired:
                log.info('Refreshing Google creds for %s', self.google_email)
                creds.refresh(httplib2.Http())
            httpauth = creds.authorize(httplib2.Http())
            return creds, httpauth
        raise Exception('Not logged into Google.')
    
    def google_service(self, service=None, version='v1'):
        """ Return gauth credentials for the specified user or None. """
        creds, httpauth = self.google_auth()
        return discovery.build(service, version, http=httpauth)

    def disconnect(self, provider):
        """ Disconnect the specified provider. """
        if provider.lower() == 'google':
            self.google_email = ''
            self.google_creds = ''
            self.save()
            log.info('Disconnected Google for %s', self.email)

    @staticmethod
    def auth_django(request, email, password):
        """ Authenticate with Django and return the user. """
        username = utils.get_object_or_none(User, email=email).username
        user = authenticate(username=username, password=password)
        if user and user.is_active:
            login(request, user)
            log.info('Logged in via Django as %s', user.email)
            return user
    
    @staticmethod
    def auth_google(request, google_code):
        """ Authenticate with Google and return the user.
            https://developers.google.com/identity/sign-in/web/server-side-flow
            https://developers.google.com/gmail/api/auth/web-server
        """
        creds = client.credentials_from_code(settings.GOOGLE_CLIENTID,
            settings.GOOGLE_SECRET, settings.GOOGLE_SCOPES, google_code)
        creds.authorize(httplib2.Http())
        google_email = creds.id_token['email']
        # Check user is currently logged in
        if request.user and request.user.is_active:
            request.user.google_email = creds.id_token['email']
            request.user.google_creds = creds.to_json()
            request.user.save()
            log.info('Connected Google account %s to userid %s', google_email, request.user)
            return request.user
        # User is not currently logged in
        user = User.objects.get(google_email=google_email)
        if user and user.is_active:
            request.user.google_creds = creds.to_json()
            login(request, user)
            log.info('Logged in via Google as %s', google_email)
            return user
    
    @staticmethod
    def logout(request):
        logout(request)
