import logging, sys
from django.conf import settings
from django.contrib.auth import get_user_model
log = logging.getLogger(__name__)


class DebugSuperuserMiddleware:
    """ Use a superuser for development requests without persisting a login. """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        enabled = settings.DEBUG and 'runserver' in sys.argv and settings.DEBUG_SUPERUSER
        if enabled and not request.user.is_authenticated:
            user = get_user_model().objects.filter(is_active=True, is_superuser=True).order_by('pk').first()
            if user is not None:
                request.user = user
                log.info('Using debug superuser %s for %s %s', user.get_username(), request.method, request.path)
        return self.get_response(request)
