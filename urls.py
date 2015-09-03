#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 Pushingkarma. All rights reserved.
"""
from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
]
