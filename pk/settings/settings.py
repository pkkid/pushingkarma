#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from .secrets import *  # noqa
import platform
from os.path import abspath, dirname, join

# Django Core Settings
HOSTNAME = platform.node()
ALLOWED_HOSTS = ['.pushingkarma.com']
BASE_DIR = dirname(dirname(abspath(__file__)))
DEBUG = HOSTNAME in ['pkkid-work', 'pkkid-home']
ROOT_URLCONF = 'pk.urls'
STATIC_URL = '/static/'
STATIC_ROOT = '%s/collectstatic/' % BASE_DIR
WSGI_APPLICATION = 'ws4redis.django_runserver.application'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Django Environment
INSTALLED_APPS = (
    #'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'django_extensions',
    'rest_framework',
    'ws4redis',
    'dbbackup',
    'pk',
)
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': ['%s/templates' % BASE_DIR],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': join(dirname(BASE_DIR), 'db.sqlite3'),
    }
}
CACHES = {'default': {
    'BACKEND': 'redis_cache.RedisCache',
    'LOCATION': 'localhost:6379',
}}
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/home/mjs7231/Logs/pushingkarma/pushingkarma.log',
            'maxBytes': 1000000,
            'backupCount': 3,
            'formatter': 'standard',
        },
    },
    'loggers': {
        'pk': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
    'formatters': {
        'standard': {
            'format': '%(asctime)-.19s %(module)12s:%(lineno)-3s %(levelname)-7s %(message)s'
        },
    },
}

# Django Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticatedOrReadOnly',),
    'PAGE_SIZE': 100
}

# Django Redis Sessions
SESSION_ENGINE = 'redis_sessions.session'
SESSION_REDIS_PREFIX = 'session'

# Django Websockets Redis
WEBSOCKET_URL = '/ws/'
WS4REDIS_CONNECTION = {'host':'localhost'}
WS4REDIS_EXPIRE = 3600
WS4REDIS_HEARTBEAT = 'heartbeat'
WS4REDIS_PREFIX = 'ws'
#WS4REDIS_ALLOWED_CHANNELS = lambda r,c: set(channels).intersection(['subscribe-broadcast'])

# DBBackup Settings
DBBACKUP_STORAGE = 'dbbackup.storage.dropbox_storage'
DBBACKUP_TOKENS_FILEPATH = '/home/mjs7231/.dbbackup'
