# encoding: utf-8
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import re_path
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from ninja import NinjaAPI
from pk.apps.main.api import router as main_router
from pk import utils

api = NinjaAPI()
api.add_router('/', utils.root_router)
api.add_router('/main', main_router)


@xframe_options_exempt
@ensure_csrf_cookie
def index(request, tmpl='index.html'):
    if url := utils.vue_devserver_running(request):
        return redirect(url)
    return utils.response(request, tmpl, {})


def api_404(request, exc=None):
    return JsonResponse({'error': 'API endpoint not found'}, status=404)


urlpatterns = [
    re_path('api/', api.urls),
    re_path(r'^api/.*$', api_404),
    re_path(r'', index, name='index'),
]


# ------------------------------
# # encoding: utf-8
# from django.http import JsonResponse
# from django.shortcuts import redirect
# from django.urls import include, path, re_path
# from django.views.decorators.clickjacking import xframe_options_exempt
# from django.views.decorators.csrf import ensure_csrf_cookie
# from pk.apps.budget import api as budget_api
# from pk.apps.main import apiviews as main_apiviews
# from pk.apps.obsidian import apiviews as obsidian_apiviews
# from pk.apps.stocks import api as stocks_api, apiviews as stocks_apiviews
# from pk.utils.apiutils import HybridRouter
# from pk import utils

# # Create Router & User APIs
# api = HybridRouter(sort_urls=True, trailing_slash=False)
# api.register('budget/accounts', budget_api.AccountsViewSet, basename='account')
# api.register('budget/categories', budget_api.CategoriesViewSet, basename='category')
# api.register('budget/transactions', budget_api.TransactionsViewSet, basename='transaction')
# api.register('stocks/tickers', stocks_api.TickerViewSet, basename='ticker')
# api.add_url('^main/generate_token$', main_apiviews.generate_token, name='main/generate_token')
# api.add_url('^main/global_vars', main_apiviews.global_vars, name='main/global_vars')
# api.add_url('^main/login$', main_apiviews.login, name='main/login')
# api.add_url('^main/logout$', main_apiviews.logout, name='main/logout')
# api.add_url('^main/user$', main_apiviews.user, name='main/user')
# api.add_url('^obsidian/note$', obsidian_apiviews.note, name='obsidian/note')
# api.add_url('^obsidian/search$', obsidian_apiviews.search, name='obsidian/search')
# api.add_url('^stocks/projection_trends$', stocks_apiviews.projection_trends, name='stocks/projection_trends')


# @xframe_options_exempt
# @ensure_csrf_cookie
# def index(request, tmpl='index.html'):
#     if url := utils.vue_devserver_running(request):
#         return redirect(url)
#     return utils.response(request, tmpl, {})


# def api_404(request, exc=None):
#     return JsonResponse({'error': 'API endpoint not found'}, status=404)


# urlpatterns = [
#     re_path(r'^api/', include(api.urls), name='api'),
#     re_path(r'^api/.*$', api_404),
#     re_path(r'', index, name='index'),
# ]
