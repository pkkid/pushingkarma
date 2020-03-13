#!/usr/bin/env python
# encoding: utf-8
from django.core.management.base import BaseCommand
from pk.utils.decorators import log_exception


class Command(BaseCommand):
    help = 'Test management command exception'

    @log_exception()
    def handle(self, *args, **kwargs):
        raise Exception('Test management command exception')
