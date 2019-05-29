# encoding: utf-8
import pk.utils.auth
from django.conf.urls import include, url
from pk import views as pk_views
from pk.apps.budget import views as budget_views
from pk.apps.notes import views as note_views
from pk.apps.stocks import views as stock_views
from rest_framework import routers

api = routers.DefaultRouter(trailing_slash=False)
api.register('user', pk_views.AccountViewSet)
api.register('notes', note_views.NotesViewSet)
api.register('accounts', budget_views.AccountsViewSet)
api.register('categories', budget_views.CategoriesViewSet)
api.register('transactions', budget_views.TransactionsViewSet)
api.register('stocks', stock_views.StocksViewSet)
api.register('keyval', budget_views.KeyValueViewSet)

urlpatterns = [
    url(r'^api', include(api.urls)),
    # url(r'^login$', pk.utils.auth.user_login, name='auth_login'),
    # url(r'^logout$', pk.utils.auth.user_logout, name='auth_logout'),
    url(r'', pk_views.index, name='index'),
]
