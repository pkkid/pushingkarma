#!/usr/bin/env python
# encoding: utf-8
import logging, os
from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from pk.utils.decorators import log_exception
from webdav3.client import Client
log = logging.getLogger('cmd')


class Command(BaseCommand):
    help = 'Backup the database to a webdav server'

    @log_exception(log)
    def handle(self, *args, **kwargs):
        localpath = settings.DATABASES['default']['NAME']
        dtstr = datetime.now().strftime(r'%Y-%m-%d')
        ext = os.path.basename(localpath).split('.')[-1]
        remotepath = settings.WEBDAV_BACKUP_DIR
        remotepath += f'/{settings.SITE_NAME}-{settings.HOSTNAME}-{dtstr}.{ext}'.lower()
        log.info('Backing up database localpath: %s; remotepath: %s', localpath, remotepath)
        client = Client(settings.WEBDAV_OPTIONS)
        client.upload_sync(local_path=localpath, remote_path=remotepath)
