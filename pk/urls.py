# encoding: utf-8
from django.conf.urls import include, url
from django.views.decorators.csrf import ensure_csrf_cookie
from pk import api as pk_api, utils
from pk.apps.budget import api as budget_api
from pk.apps.calendar import views as calendar_views
from pk.apps.notes import api as note_api
from pk.apps.stocks import views as stock_views
from rest_framework import routers

api = routers.DefaultRouter(trailing_slash=False)
api.register('user', pk_api.AccountViewSet)
api.register('notes', note_api.NotesViewSet)
api.register('accounts', budget_api.AccountsViewSet)
api.register('categories', budget_api.CategoriesViewSet)
api.register('transactions', budget_api.TransactionsViewSet)
api.register('stocks', stock_views.StocksViewSet)
api.register('keyval', budget_api.KeyValueViewSet)

@ensure_csrf_cookie
def index(request, tmpl='index.html'):
    return utils.response(request, tmpl, {})

urlpatterns = [
    url(r'^api/', include(api.urls)),
    url(r'^calendar/$', calendar_views.calendar, name='calendar'),
    url(r'', index, name='index'),
]
