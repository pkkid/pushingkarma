# encoding: utf-8
import logging, sys
from django.apps import AppConfig
log = logging.getLogger(__name__)


class MainConfig(AppConfig):
    name = 'pk.apps.main'

    def ready(self):
        argstr = ' '.join(sys.argv).lower()
        if 'uvicorn' in argstr or 'daphne' in argstr or 'hypercorn' in argstr:
            log.info('---')
            log.info('Starting Django ASGI server')
        if 'gunicorn' in argstr or 'uwsgi' in argstr or 'mod_wsgi' in argstr:
            log.info('---')
            log.info('Starting Django WSGI server')
