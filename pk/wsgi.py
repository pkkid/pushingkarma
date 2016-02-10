#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'pk.settings.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
