# encoding: utf-8
from django.conf.urls import include, url
from django.views.decorators.csrf import ensure_csrf_cookie
from pk import api as pk_api, utils
from pk.apps.budget import api as budget_api
from pk.apps.tools import api as tools_api
from pk.apps.notes import api as note_api
from pk.apps.stocks import api as stock_api
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
api.register('budget/keyval', budget_api.KeyValueViewSet)
api.add_url('^budget/upload$', budget_api.upload, name='budget/upload')
# Stocks API
api.add_url('^stocks$', stock_api.stocks, name='stocks')
api.register('stocks/list', stock_api.StocksViewSet)
api.add_url('^stocks/csv$', stock_api.csv, name='stocks/csv')
# Tools API
api.add_url('^tools$', tools_api.tools, name='tools')
api.add_url('^tools/events$', tools_api.events, name='tools/events')
api.add_url('^tools/ical$', tools_api.ical, name='tools/ical')
api.add_url('^tools/news$', tools_api.news, name='tools/news')
api.add_url('^tools/photo$', tools_api.photo, name='tools/photo')
api.add_url('^tools/tasks$', tools_api.tasks, name='tools/tasks')
api.add_url('^tools/weather$', tools_api.weather, name='tools/weather')
# Misc APIs
api.register('notes', note_api.NotesViewSet)


@ensure_csrf_cookie
def index(request, tmpl='index.html'):
    return utils.response(request, tmpl, {})

urlpatterns = [
    url(r'^api/', include(api.urls), name='api'),
    url(r'', index, name='index'),
]
