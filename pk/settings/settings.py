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
    'redsocks',
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
        'redsocks': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        }
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
WSGI_APPLICATION = 'redsocks.runserver.server.application'
WEBSOCKET_URL = '/ws/'
REDSOCKS_CONNECTION = {'host':'localhost'}
REDSOCKS_EXPIRE = 3600
REDSOCKS_HEARTBEAT = 'heartbeat'
REDSOCKS_PREFIX = 'ws'
REDSOCKS_SUBSCRIBERS = {
    'magnets': 'pk.websocket.magnets.MagnetsSubscriber',
}
#REDSOCKS_ALLOWED_CHANNELS = 'pk.websocket.subscriber.allowed_channels'

# DBBackup Settings
DBBACKUP_STORAGE = 'storages.backends.sftpstorage.SFTPStorage'
DBBACKUP_STORAGE_OPTIONS = {
    'root_path': '/home',
    'host': DBBACKUP_SFTP_HOST,
    'params': {
        'username': DBBACKUP_SFTP_USER,
        'password': DBBACKUP_SFTP_PASS,
        'port': DBBACKUP_SFTP_PORT,
        'allow_agent': False,
        'look_for_keys': False,
    },
}
