# Exposes the ASGI callable as a module-level variable named ``application``.
# https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pk.settings.settings')
application = get_wsgi_application()
