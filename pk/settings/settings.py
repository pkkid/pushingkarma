#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from .secrets import *  # noqa
import platform
import debug_toolbar.middleware
from os.path import abspath, dirname, join

# Django Core Settings
HOSTNAME = platform.node()
ALLOWED_HOSTS = []
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


# DBBackup Settings
DBBACKUP_BACKUP_DIRECTORY = '/home/mjs7231/Dropbox/Backup/pushingkarma/'
DBBACKUP_FILENAME_TEMPLATE = '{servername}-{datetime}.{extension}'


# Debug Settings
if DEBUG:
    INSTALLED_APPS = INSTALLED_APPS + (
        #'django.contrib.staticfiles',
        'debug_toolbar',
    )

    DEBUG_TOOLBAR_CONFIG = {'INTERCEPT_REDIRECTS': False}
    def show_toolbar_monkeypatch(request):  # noqa
        if request.META.get('REMOTE_ADDR', None) not in INTERNAL_IPS: return False
        if request.is_ajax(): return False
        return request.GET.get('debug')
    debug_toolbar.middleware.show_toolbar = show_toolbar_monkeypatch
