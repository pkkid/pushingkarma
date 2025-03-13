# encoding: utf-8
from django.shortcuts import redirect
from django.urls import include, re_path
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from pk.apps.main import apiviews as main_apiviews
from pk.apps.obsidian import apiviews as obsidian_apiviews
from pk.apps.budget import api as budget_api
from pk.apps.stocks import api as stocks_api
from pk.utils.apiutils import HybridRouter
from pk import utils

# Create Router & User APIs
api = HybridRouter(sort_urls=True, trailing_slash=False)
api.register('budget/accounts', budget_api.AccountsViewSet)
api.register('budget/categories', budget_api.CategoriesViewSet)
api.register('budget/transactions', budget_api.TransactionsViewSet)
api.register('stocks/tickers', stocks_api.TickerViewSet)
api.add_url('^main/gentoken$', main_apiviews.generate_token, name='main/gentoken')
api.add_url('^main/globalvars', main_apiviews.globalvars, name='main/globalvars')
api.add_url('^main/login$', main_apiviews.login, name='main/login')
api.add_url('^main/logout$', main_apiviews.logout, name='main/logout')
api.add_url('^main/user$', main_apiviews.user, name='main/user')
api.add_url('^obsidian/note$', obsidian_apiviews.note, name='obsidian/note')
api.add_url('^obsidian/search$', obsidian_apiviews.search, name='obsidian/search')


@xframe_options_exempt
@ensure_csrf_cookie
def index(request, tmpl='index.html'):
    if url := utils.vue_devserver_running(request):
        return redirect(url)
    return utils.response(request, tmpl)


urlpatterns = [
    re_path(r'^api/', include(api.urls), name='api'),
    re_path(r'', index, name='index'),
]
