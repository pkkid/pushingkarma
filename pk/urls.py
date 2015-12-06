#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
import pk.api, pk.views, pk.utils.auth
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import RedirectView, TemplateView
from rest_framework import routers

redirect = lambda url: RedirectView.as_view(url=url, permanent=False)
template = lambda tmpl: TemplateView.as_view(template_name=tmpl)

api = routers.DefaultRouter()
api.register('notes', pk.api.NotesViewSet)
api.register('pages', pk.api.PagesViewSet)

urlpatterns = [
    # includes
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(api.urls)),
    # misc utils
    url(r'^404/$', template('404.html'), name='404'),
    url(r'^500/$', template('500.html'), name='500'),
    url(r'^auth/login/$', pk.utils.auth.user_login, name='auth_login'),
    url(r'^auth/logout/$', pk.utils.auth.user_logout, name='auth_logout'),
    url(r'^favicon\.ico$', redirect('/static/img/favicon.ico'), name='favicon'),
    # pushingKarma
    url(r'^$', pk.views.page, name='index'),
    url(r'^n/$', pk.views.note, name='notebook'),
    url(r'^p/(?P<slug>.*?)/$', pk.views.page, name='page'),
    url(r'^n/(?P<slug>.*?)/$', pk.views.note, name='note'),
    url(r'^markdown/$', pk.views.markdown, name='markdown'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT, show_indexes=True)
