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
STATIC_ROOT = '%s/static/' % BASE_DIR
WSGI_APPLICATION = 'pk.wsgi.application'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Django Environment
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'django_extensions',
    'rest_framework',
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
    'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
    'LOCATION': 'django_cache',
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
            'filename': join(dirname(BASE_DIR), 'pk.log'),
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

# DBBackup Settings
DBBACKUP_STORAGE = 'dbbackup.storage.dropbox_storage'
DBBACKUP_TOKENS_FILEPATH = '/home/mjs7231/.dbbackup'

#DBBACKUP_BACKUP_DIRECTORY = '/home/mjs7231/Dropbox/Backup/pushingkarma/'
#DBBACKUP_FILENAME_TEMPLATE = '{servername}-{datetime}.{extension}'
