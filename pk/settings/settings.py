# encoding: utf-8
import platform
from os import makedirs
from os.path import abspath, dirname
try:
    from .secrets import *  # noqa
except ImportError:
    raise SystemExit('Error: Secrets file not present.')

# Django Core Settings
HOSTNAME = platform.node()
SITE_NAME = 'PushingKarma'
ALLOWED_HOSTS = ['.pushingkarma.com', 'localhost', '127.0.0.1']
BASE_DIR = dirname(dirname(dirname(abspath(__file__))))
LOG_DIR = f'{BASE_DIR}/pk/_logs'
DEBUG = HOSTNAME in ['meshy']
ROOT_URLCONF = 'pk.urls'
LOGIN_URL = 'index'
STATIC_URL = '/static/'
STATIC_ROOT = f'{BASE_DIR}/pk/_static/'
STATICFILES_DIRS = [f'{BASE_DIR}/pk/_dist']
INTERNAL_IPS = ['127.0.0.1']
DOMAIN = 'http://localhost:8000' if DEBUG else 'https://pushingkarma.com'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'US/Eastern'
USE_I18N = True
USE_L10N = True
USE_TZ = True

INSTALLED_APPS = (
    'corsheaders',
    'django_extensions',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'rest_framework.authtoken',
    'rest_framework',
    'pk',
    'pk.apps.budget',
    'pk.apps.notes',
    'pk.apps.stocks',
    'pk.apps.tools',
    'pk.apps.user',
)
AUTH_USER_MODEL = 'user.User'
MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
)
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [f'{BASE_DIR}/pk/templates', f'{BASE_DIR}/pk/_dist'],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]
DATABASES = {'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': f'{BASE_DIR}/pk/db.sqlite3',
}}

# Django Cache
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
CACHES = {'default': {
    'BACKEND': 'redis_cache.RedisCache',
    'LOCATION': ['%s:%s' % (REDIS_HOST, REDIS_PORT)],
    'OPTIONS': {'DB':0},
}}

# Logging
makedirs(LOG_DIR, exist_ok=True)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'console': {'level':'INFO', 'class':'logging.StreamHandler', 'formatter':'standard'},
        'file': {'level':'INFO', 'class':'logging.handlers.RotatingFileHandler', 'formatter':'standard',
            'filename': f'{LOG_DIR}/django.log', 'maxBytes':1000000, 'backupCount':3},
        'email': {'level':'ERROR', 'class':'pk.utils.logging.CustomEmailHandler'},
    },
    'loggers': {
        'cmd': {'handlers':['email','console'], 'level':'INFO', 'propagate':True},
        'pk': {'handlers':['file','email','console'], 'level':'INFO', 'propagate':True},
    },
    'formatters':{
        'standard':{'format':'%(asctime)-.19s %(module)12s:%(lineno)-3s %(levelname)-7s %(message)s'}
    },
}

# Django Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework.authentication.SessionAuthentication'],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticatedOrReadOnly'],
    'DEFAULT_PAGINATION_CLASS': 'pk.utils.api.pagination.CustomPageNumberPagination',
    'EXCEPTION_HANDLER': 'pk.utils.api.custom_exception_handler',
}

# Django Redis Sessions
SESSION_ENGINE = 'redis_sessions.session'
SESSION_COOKIE_AGE = 7776000            # 90 days
SESSION_COOKIE_SAMESITE = 'Strict'      # Prevents sending to cross-site domains
CSRF_COOKIE_SAMESITE = 'Strict'         # Prevents sending to cross-site domains

# Django-cors-headers - Cross-Origin Resource Sharing
CORS_ORIGIN_WHITELIST = []
CORS_ALLOW_METHODS = ['GET']
