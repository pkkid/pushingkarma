#!/usr/bin/env python
# encoding: utf-8
import pk.utils.auth
from django.conf.urls import include, url
from django.views.generic import RedirectView, TemplateView
from pk import views as pk_views
from pk.apps.budget import views as budget_views
from pk.apps.calendar import views as calendar_views
from pk.apps.focus import views as focus_views
from pk.apps.notes import views as note_views
from pk.apps.pages import views as page_views
from pk.apps.stocks import views as stock_views
from rest_framework import routers

redirect = lambda url: RedirectView.as_view(url=url, permanent=False)
template = lambda tmpl: TemplateView.as_view(template_name=tmpl)

api = routers.DefaultRouter(trailing_slash=False)
api.register('user', pk_views.AccountViewSet)
api.register('pages', page_views.PagesViewSet)
api.register('notes', note_views.NotesViewSet)
api.register('accounts', budget_views.AccountsViewSet)
api.register('categories', budget_views.CategoriesViewSet)
api.register('transactions', budget_views.TransactionsViewSet)
api.register('stocks', stock_views.StocksViewSet)
api.register('keyval', budget_views.KeyValueViewSet)

urlpatterns = [
    url(r'^api/', include(api.urls)),
    url(r'^404/$', template('404.html'), name='404'),
    url(r'^500/$', template('500.html'), name='500'),
    url(r'^auth/login/$', pk.utils.auth.user_login, name='auth_login'),
    url(r'^auth/logout/$', pk.utils.auth.user_logout, name='auth_logout'),
    url(r'^favicon\.ico$', redirect('/static/site/img/favicon.ico'), name='favicon'),
    url(r'^markdown/p/$', page_views.markdown, name='page_markdown'),
    url(r'^markdown/n/$', note_views.markdown, name='note_markdown'),
    url(r'^calendar/$', calendar_views.calendar, name='calendar'),
    url(r'^focus/$', focus_views.focus, name='focus'),
    url(r'^raspi/$', focus_views.raspi, name='raspi'),
    url(r'^$', pk_views.index, name='index'),
]
