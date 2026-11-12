# encoding: utf-8
import secrets, string
from django.conf import settings
from django.db import models
from pk.utils.django import TimeStampedModel
APIKEY_LENGTH = 25  # Letters and digits, about 148 bits of randomness
APIKEY_CHARS = string.ascii_letters + string.digits


class ApiKey(TimeStampedModel):
    """ A single api key per user. Sending it as the apikey url argument or the X-Apikey
        header authenticates the request as that user (see ApiKeyMiddleware). The key is
        stored as plain text so the account panel can keep displaying it.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='apikey', on_delete=models.CASCADE)
    key = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f'<ApiKey:{self.user.username}:{self.key[:6]}...>'

    @classmethod
    def regenerate(cls, user):
        """ Create a new key for the user, replacing (and revoking) any existing key. """
        key = ''.join(secrets.choice(APIKEY_CHARS) for _ in range(APIKEY_LENGTH))
        apikey, _ = cls.objects.update_or_create(user=user, defaults={'key': key})
        return apikey
