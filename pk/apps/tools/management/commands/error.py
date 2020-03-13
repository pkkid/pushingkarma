#!/usr/bin/env python
# encoding: utf-8
import logging
from django.core.management.base import BaseCommand
from pk.utils.decorators import log_exception
log = logging.getLogger('cmd')


class Command(BaseCommand):
    help = 'Test management command exception'

    @log_exception(log)
    def handle(self, *args, **kwargs):
        raise Exception('Test management command exception')
