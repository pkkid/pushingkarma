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
    url(r'^auth/login/$', 'pk.utils.auth.user_login', name='auth_login'),
    url(r'^auth/logout/$', 'pk.utils.auth.user_logout', name='auth_logout'),
    url(r'^favicon\.ico$', redirect('/static/img/favicon.ico'), name='favicon'),

    # PushingKarma
    url(r'^$', 'pk.views.cms', name='index'),
    url(r'^p/(?P<slug>.*?)/$', 'pk.views.cms', name='page'),
    url(r'^markdown/$', 'pk.views.markdown', name='markdown'),
    url(r'^notebook/$', 'pk.views.notebook', name='notebook'),

]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT, show_indexes=True)
