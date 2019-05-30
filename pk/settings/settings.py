# encoding: utf-8
import platform
from os import makedirs
from os.path import abspath, dirname, join
try:
    from .secrets import *  # noqa
except ImportError:
    raise SystemExit('Error: Secrets file not present.')

# Django Core Settings
HOSTNAME = platform.node()
SITE_NAME = 'PushingKarma'
ALLOWED_HOSTS = ['.pushingkarma.com', 'localhost', '127.0.0.1']
BASE_DIR = dirname(dirname(dirname(abspath(__file__))))
LOG_DIR = join(BASE_DIR, 'pk/.data')
DEBUG = HOSTNAME in ['pkkid-work', 'pkkid-home']
ROOT_URLCONF = 'pk.urls'
LOGIN_URL = 'index'
STATIC_URL = '/static/'
STATIC_ROOT = join(BASE_DIR, 'pk/collectstatic/')
STATICFILES_DIRS = [join(BASE_DIR, 'vue/dist/')]
INTERNAL_IPS = ['127.0.0.1']

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'US/Eastern'
USE_I18N = True
USE_L10N = True
USE_TZ = True

INSTALLED_APPS = (
    # 'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'django_extensions',
    'corsheaders',
    'rest_framework',
    'graphene_django',
    'redsocks',
    'pk',
    'pk.apps.budget',
    'pk.apps.focus',
    'pk.apps.notes',
    'pk.apps.stocks',
)
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
    'DIRS': [
        join(BASE_DIR, 'pk/templates'),
        join(BASE_DIR, 'vue/dist'),
    ],
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
    'NAME': join(BASE_DIR, 'pk/.data/db.sqlite3'),
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
LOGLEVEL = 'INFO'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'console': {'level':LOGLEVEL, 'class':'logging.StreamHandler', 'formatter':'standard'},
        'file': {'level': LOGLEVEL, 'class':'logging.handlers.RotatingFileHandler',
            'filename':join(LOG_DIR, 'django.log'), 'maxBytes':1000000, 'backupCount':3,
            'formatter': 'standard'},
    },
    'loggers': {
        'pk': {'handlers':['file', 'console'], 'level':LOGLEVEL, 'propagate':True},
        'redsocks': {'handlers':['file', 'console'], 'level':LOGLEVEL, 'propagate':False},
    },
    'formatters':{
        'standard':{'format':'%(asctime)-.19s %(module)12s:%(lineno)-3s %(levelname)-7s %(message)s'}
    },
}

# Django Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticatedOrReadOnly',),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
}

# Django Redis Sessions
SESSION_ENGINE = 'redis_sessions.session'
SESSION_COOKIE_AGE = 7776000  # 90 days

# Django Websockets Redis
WEBSOCKET_URL = '/ws/'
WSGI_APPLICATION = 'redsocks.runserver.server.application'
REDSOCKS_ALLOWED_CHANNELS = 'pk.websocket.subscriber.allowed_channels'
REDSOCKS_CONNECTION = {'host':REDIS_HOST}
REDSOCKS_EXPIRE = 3600
REDSOCKS_HEARTBEAT = 'heartbeat'
REDSOCKS_PREFIX = 'ws'
REDSOCKS_SUBSCRIBERS = {
    'magnets': 'pk.apps.magnets.websock.MagnetsSubscriber',
}

# Django-cors-headers - Cross-Origin Resource Sharing
CORS_ORIGIN_WHITELIST = ['bugs.nasuni.net']
CORS_ALLOW_METHODS = ['GET']
