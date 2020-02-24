# encoding: utf-8
from django.conf.urls import include, url
from django.views.decorators.csrf import ensure_csrf_cookie
from pk import api as pk_api, utils
from pk.apps.budget import api as budget_api
from pk.apps.tools import api as tools_api
from pk.apps.notes import api as note_api
from pk.apps.stocks import views as stock_views
from pk.utils.api import HybridRouter

# Create Router & User APIs
api = HybridRouter(sort_urls=True, trailing_slash=False)
api.add_url('^user$', pk_api.user, name='user')
api.add_url('^user/login$', pk_api.login, name='user/login')
api.add_url('^user/gentoken$', pk_api.gen_token, name='user/gentoken')
api.add_url('^user/logout$', pk_api.logout, name='user/logout')
# Budget API
api.add_url('^budget$', budget_api.budget, name='budget')
api.register('budget/accounts', budget_api.AccountsViewSet)
api.register('budget/categories', budget_api.CategoriesViewSet)
api.register('budget/transactions', budget_api.TransactionsViewSet)
# Misc APIs
api.register('notes', note_api.NotesViewSet)
api.register('stocks', stock_views.StocksViewSet)
api.register('keyval', budget_api.KeyValueViewSet)
api.add_url('^events$', tools_api.events, name='events')
api.add_url('^news$', tools_api.news, name='news')
api.add_url('^photo$', tools_api.photo, name='photo')
api.add_url('^tasks$', tools_api.tasks, name='tasks')
api.add_url('^weather$', tools_api.weather, name='weather')


@ensure_csrf_cookie
def index(request, tmpl='index.html'):
    return utils.response(request, tmpl, {})

urlpatterns = [
    url(r'^api/', include(api.urls), name='api'),
    # from pk.apps.calendar import views as calendar_views
    # url(r'^calendar/$', calendar_views.calendar, name='calendar'),
    url(r'', index, name='index'),
]
