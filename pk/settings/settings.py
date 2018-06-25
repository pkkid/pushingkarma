#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
import platform
from os import makedirs
from os.path import abspath, dirname, expanduser, join
from . import secrets

# Django Core Settings
HOSTNAME = platform.node()
ALLOWED_HOSTS = ['.pushingkarma.com', 'localhost']
BASE_DIR = dirname(dirname(abspath(__file__)))
DEBUG = HOSTNAME in ['pkkid-work3', 'pkkid-home']
ROOT_URLCONF = 'pk.urls'
LOGIN_URL = 'index'
STATIC_URL = '/static/'
STATIC_ROOT = '%s/collectstatic/' % BASE_DIR
SECRET_KEY = secrets.SECRET_KEY
INTERNAL_IPS = ['127.0.0.1']

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
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
    'rest_framework',
    'redsocks',
    'dbbackup',
    'pk',
    'pk.apps.budget',
    'pk.apps.notes',
    'pk.apps.pages',
)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    # 'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    # 'pk.utils.middleware.CleanHTMLMiddleware',
)

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': ['%s/templates' % BASE_DIR],
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
    'NAME': join(dirname(BASE_DIR), 'db.sqlite3'),
}}

LOGLEVEL = 'INFO'
LOGFORMAT = '%(asctime)-.19s %(module)12s:%(lineno)-3s %(levelname)-7s %(message)s'
LOGDIR = '/home/mjs7231/Logs/pushingkarma/'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'console': {'level':LOGLEVEL, 'class':'logging.StreamHandler', 'formatter':'standard'},
        'file': {'level': LOGLEVEL, 'class':'logging.handlers.RotatingFileHandler',
            'filename':join(LOGDIR,'pushingkarma.log'), 'maxBytes':1000000, 'backupCount':3,
            'formatter': 'standard'},
    },
    'loggers': {
        'pk': {'handlers':['file','console'], 'level':LOGLEVEL, 'propagate':True},
        'redsocks': {'handlers':['file','console'], 'level':LOGLEVEL, 'propagate':False},
    },
    'formatters':{'standard':{'format':LOGFORMAT}},
}
makedirs(LOGDIR, exist_ok=True)

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
REDSOCKS_ALLOWED_CHANNELS = 'pk.websocket.subscriber.allowed_channels'
WSGI_APPLICATION = 'redsocks.runserver.server.application'
WEBSOCKET_URL = '/ws/'
REDSOCKS_CONNECTION = {'host':'localhost'}
REDSOCKS_EXPIRE = 3600
REDSOCKS_HEARTBEAT = 'heartbeat'
REDSOCKS_PREFIX = 'ws'
REDSOCKS_SUBSCRIBERS = {
    'magnets': 'pk.websocket.magnets.MagnetsSubscriber',
}

# DBBackup Settings
DBBACKUP_STORAGE = 'storages.backends.sftpstorage.SFTPStorage'
DBBACKUP_STORAGE_OPTIONS = {
    'root_path': '/home',
    'host': secrets.DBBACKUP_SFTP_HOST,
    'params': {
        'username': secrets.DBBACKUP_SFTP_USER,
        'password': secrets.DBBACKUP_SFTP_PASS,
        'port': secrets.DBBACKUP_SFTP_PORT,
        'allow_agent': False,
        'look_for_keys': False,
    },
}
