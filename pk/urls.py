# encoding: utf-8
from django.shortcuts import redirect
from django.urls import include, re_path
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from pk.apps.user import api as user_api
from pk.apps.budget import api as budget_api
from pk.apps.tools import api as tools_api
from pk.apps.notes import api as note_api
from pk.apps.stocks import api as stock_api
from pk.utils.apiutils import HybridRouter
from pk import utils

# Create Router & User APIs
api = HybridRouter(sort_urls=True, trailing_slash=False)
api.register('budget/accounts', budget_api.AccountsViewSet)
api.register('budget/categories', budget_api.CategoriesViewSet)
api.register('budget/transactions', budget_api.TransactionsViewSet)
api.register('notes', note_api.NotesViewSet)
api.register('stocks/list', stock_api.StocksViewSet)
api.add_url('^budget/history', budget_api.history, name='budget/history')
api.add_url('^budget/summary', budget_api.summary, name='budget/summary')
api.add_url('^budget/upload$', budget_api.upload, name='budget/upload')
api.add_url('^budget$', budget_api.budget, name='budget')
api.add_url('^stocks/csv$', stock_api.csv, name='stocks/csv')
api.add_url('^stocks$', stock_api.stocks, name='stocks')
api.add_url('^tools/error$', tools_api.error, name='tools/error')
api.add_url('^tools/events$', tools_api.events, name='tools/events')
api.add_url('^tools/news$', tools_api.news, name='tools/news')
api.add_url('^tools/photo$', tools_api.photo, name='tools/photo')
api.add_url('^tools/tasks$', tools_api.tasks, name='tools/tasks')
api.add_url('^tools/weather$', tools_api.weather, name='tools/weather')
api.add_url('^tools$', tools_api.tools, name='tools')
api.add_url('^user/disconnect$', user_api.disconnect, name='user/disconnect')
api.add_url('^user/gentoken$', user_api.generate_token, name='user/gentoken')
api.add_url('^user/login$', user_api.login, name='user/login')
api.add_url('^user/logout$', user_api.logout, name='user/logout')
api.add_url('^user$', user_api.user, name='user')


@xframe_options_exempt
@ensure_csrf_cookie
def index(request, tmpl='index.html'):
    if url := utils.vue_devserver_running(request):
        return redirect(url)
    return utils.response(request, tmpl, {})


urlpatterns = [
    re_path(r'^api/', include(api.urls), name='api'),
    re_path(r'', index, name='index'),
]
