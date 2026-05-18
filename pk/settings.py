# encoding: utf-8
import os
import platform
from os import makedirs
from os.path import abspath, dirname, expanduser
from corsheaders.defaults import default_headers
from dotenv import load_dotenv

_to_bool = lambda v: str(v).strip().lower() in ['true', '1', 'yes', 't']
_to_list = lambda v: [item.strip() for item in v.split(',') if item.strip()]

# Django Core Settings
# https://docs.djangoproject.com/en/5.0/topics/settings/
BASE_DIR = dirname(dirname(abspath(__file__)))
load_dotenv(f'{BASE_DIR}/.env')
HOSTNAME = platform.node()
DEBUG = _to_bool(os.getenv('DEBUG'))
ROOT_URLCONF = 'pk.urls'
SECRET_KEY = os.getenv('SECRET_KEY')
WSGI_APPLICATION = 'pk.wsgi.application'

# Domain, Allowed Hosts and Internal IPs
# DOMAIN is my own settings used for reverse URL lookups
# https://docs.djangoproject.com/en/2.0/ref/settings/#allowed-hosts
# https://docs.djangoproject.com/en/2.0/ref/settings/#internal-ips
DOMAIN = os.getenv('DOMAIN')
ALLOWED_HOSTS = _to_list(os.getenv('ALLOWED_HOSTS'))
INTERNAL_IPS = _to_list(os.getenv('INTERNAL_IPS'))

# Global Variables
# Variables shared with the Vue application
GLOBALVARS = {'DEBUG':DEBUG, 'DOMAIN':DOMAIN}

# Static Files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = 'static/'
STATIC_ROOT = f'{BASE_DIR}/_static/'
STATICFILES_DIRS = [f'{BASE_DIR}/_dist/static']

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/New_York'
USE_I18N = True
USE_TZ = True

# Application definition
# https://docs.djangoproject.com/en/5.0/ref/settings/#installed-apps
# https://github.com/adamchainz/django-cors-headers
TEMPLATES = []
INSTALLED_APPS = (
    'corsheaders',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'pk.apps.main',
    'pk.apps.obsidian',
    'pk.apps.budget',
    'pk.apps.stocks',
)
MIDDLEWARE = (
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'pk.utils.django.QueryCounterMiddleware',
)
DATABASES = {'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': f'{BASE_DIR}/pk/db.sqlite3',
}}

# Django Cache Settings
# https://docs.djangoproject.com/en/5.1/topics/cache/
CACHES = {'default': {
    'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
    'LOCATION': 'django_cache',
}}

# Additional Database Settings
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django Sessions
# https://docs.djangoproject.com/en/5.0/topics/http/sessions/
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 7776000  # 90 days
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_SECURE = True
if DEBUG is True:
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False
    
# CSRF Settings
# https://docs.djangoproject.com/en/5.0/ref/csrf/
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = ['http://localhost:5173', 'http://localhost.localdomain:5173']
if DEBUG is True:
    CSRF_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SECURE = False

# CORS Settings
# https://github.com/adamchainz/django-cors-headers
CORS_ORIGIN_WHITELIST = CSRF_TRUSTED_ORIGINS
CORS_ALLOW_METHODS = ['GET', 'POST', 'PATCH', 'DELETE', 'OPTIONS']
CORS_ALLOW_CREDENTIALS = True
CORS_EXPOSE_HEADERS = ['Allow', 'Response-Time', 'Queries']
CORS_ALLOW_HEADERS = list(default_headers) + ['Count-Queries', 'Log-Queries']
if DEBUG: CORS_ALLOW_ALL_ORIGINS = True

# Query Counter
# Custom middleware to summarize db queries. ENABLE values can be None, True,
# or False. None means the headers must ask for it. Setting True or False will
# ignore the headers and force enable or disable the feature.
QUERYCOUNTER_ENABLE_HEADERS = None
QUERYCOUNTER_ENABLE_LOG = None
QUERYCOUNTER_SIMPLIFY_SQL = True

# Email Settings
# https://docs.djangoproject.com/en/5.0/topics/email/
EMAIL = os.getenv('EMAIL')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
ADMINS = [('Michael Shepanski', EMAIL_HOST_USER)]

# Obsidian Notes
# Path to Obsidian markdown files
OBSIDIAN_BUCKETS = {}
OBSIDIAN_BUCKETS['public'] = {
    'vault': 'Notes',
    'root': '/notes',
    'path': '/notes/PushingKarma',
}
OBSIDIAN_BUCKETS['private'] = {
    'vault': 'Notes',
    'root': '/notes',
    'path': '/notes/Private',
    'check_permission': lambda user: user.is_authenticated,
}
if DEBUG is True:
    OBSIDIAN_BUCKETS['public']['root'] = expanduser('~/Sync/Notes')
    OBSIDIAN_BUCKETS['public']['path'] = expanduser('~/Sync/Notes/PushingKarma')
    OBSIDIAN_BUCKETS['private']['root'] = expanduser('~/Sync/Notes')
    OBSIDIAN_BUCKETS['private']['path'] = expanduser('~/Sync/Notes/Private')

# Reddit (using PRAW)
# https://github.com/praw-dev/praw
REDDIT_AUTH = {
    'client_id': os.getenv('REDDIT_CLIENT_ID'),
    'client_secret': os.getenv('REDDIT_CLIENT_SECRET'),
    'username': os.getenv('REDDIT_USERNAME'),
    'password': os.getenv('REDDIT_PASSWORD'),
    'user_agent': platform.node()
}

# AI Prompt Settings
# AI and Gemini Settings
AIPROMPT_TIMEOUT = 45
AIPROMPT_MAX_CHARS = 4000
AIPROMPT_MAX_RESPONSE = 20000
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = os.getenv('GEMINI_MODEL')

# Logging
# https://docs.djangoproject.com/en/5.0/topics/logging/
LOGDIR = f'{BASE_DIR}/_logs'
LOGLEVEL = 'DEBUG' if DEBUG else 'INFO'
LOGFORMAT = '%(asctime)-.19s %(module)16s:%(lineno)-3s %(levelname)-7s %(message)s'
makedirs(LOGDIR, exist_ok=True)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters':{
        'default':{'format':LOGFORMAT},
        'colored': {'()':'pk.utils.logging.ColoredFormatter', 'fmt':LOGFORMAT},
    },
    'handlers': {
        'default': {'class':'logging.handlers.RotatingFileHandler', 'filename':f'{LOGDIR}/django.log',
            'level':'DEBUG', 'formatter':'colored', 'backupCount':5, 'maxBytes':10000000},
        'stdout': {'level':'DEBUG', 'class':'logging.StreamHandler', 'formatter':'colored'},
    },
    'loggers': {
        '': {'handlers':['default','stdout'], 'level':LOGLEVEL, 'propagate':True},
        'asyncio': {'handlers':['default','stdout'], 'level':'ERROR', 'propagate':True},
        'connectionpool': {'handlers':['default','stdout'], 'level':'ERROR', 'propagate':True},
        'sessions': {'handlers':['default','stdout'], 'level':'ERROR', 'propagate':True},
        'exifread': {'handlers':['default','stdout'], 'level':'ERROR', 'propagate':True},
        'ofxtools': {'handlers':['default','stdout'], 'level':'ERROR', 'propagate':True},
    },
}
