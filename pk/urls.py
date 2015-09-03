#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import RedirectView, TemplateView

redirect = lambda url: RedirectView.as_view(url=url)
template = lambda tmpl: TemplateView.as_view(template_name=tmpl)

urlpatterns = [
    # Includes
    url(r'^admin/', include(admin.site.urls)),

    # Misc Utils
    url(r'^404/$', template('404.html'), name='404'),
    url(r'^500/$', template('500.html'), name='500'),
    url(r'^auth/login/$', 'pushingkarma.utils.auth.user_login', name='auth_login'),
    url(r'^auth/logout/$', 'pushingkarma.utils.auth.user_logout', name='auth_logout'),
    url(r'^favicon\.ico$', redirect('/static/img/icon/favicon.ico'), name='favicon'),

    # PushingKarma
    url(r'^$', 'pushingkarma.views.notebook.overview', name='index'),
    url(r'^notebook/$', 'pushingkarma.views.notebook.overview', name='notebook'),
    url(r'^projects/$', 'pushingkarma.views.projects.overview', name='projects'),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT, show_indexes=True)
