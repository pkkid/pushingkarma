# encoding: utf-8
import logging
from django.conf import settings
from .models import ApiKey
log = logging.getLogger(__name__)


class ApiKeyMiddleware:
    """ Authenticate the request as the key's user when an api key is sent as the apikey
        url argument or the X-Apikey header. Keys are only accepted over HTTPS unless DEBUG
        is enabled, so they never travel unencrypted in production. Sets request.apikey_auth
        so the api auth (pk.utils.ninja.user_auth) can skip the session CSRF check.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        key = request.GET.get('apikey') or request.META.get('HTTP_X_APIKEY')
        request.apikey_auth = False
        if key and not (request.is_secure() or settings.DEBUG):
            log.warning(f'Ignoring api key sent over insecure connection: {request.path}')
        elif key:
            apikey = ApiKey.objects.select_related('user').filter(key=key, user__is_active=True).first()
            if apikey:
                request.user = apikey.user
                request.apikey_auth = True
            else:
                log.warning(f'Invalid api key: {request.path}')
        return self.get_response(request)
