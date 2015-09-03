#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 Pushingkarma. All rights reserved.
"""
import os, sys


sys.path.insert(0, os.path.expandvars('$HOME/Projects'))
sys.path.insert(1, os.path.expandvars('$HOME/.virtualenvs/pushingkarma/lib/python3.4/site-packages'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pushingkarma.settings.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
