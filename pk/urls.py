# encoding: utf-8
import logging
from django.shortcuts import redirect, render
from django.urls import re_path
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from http import HTTPStatus
from ninja import NinjaAPI
from ninja.errors import HttpError
from pk.utils import django_utils, ninja_utils
from pk.apps.main.api import router as main_router
from pk.apps.obsidian.api import router as obsidian_router
from pk.apps.stocks.api import router as stocks_router
log = logging.getLogger(__name__)

api = NinjaAPI(urls_namespace='api')
api.add_router('/', ninja_utils.root_router)
api.add_router('/main', main_router)
api.add_router('/obsidian', obsidian_router)
api.add_router('/stocks', stocks_router)


@xframe_options_exempt
@ensure_csrf_cookie
def index(request, tmpl='index.html'):
    if url := django_utils.vue_devserver_running(request):
        return redirect(url)
    return render(request, tmpl, {})


@api.exception_handler(Exception)
def api_exception(request, err):
    status = getattr(err, 'status_code', 500)
    phrase = HTTPStatus(status).phrase
    data = dict(status=phrase, message=str(err))
    if status == 500: log.exception(err)
    return api.create_response(request, data, status=status)


def api_404(request, exc=None):
    return api_exception(request, HttpError(404, 'API endpoint not found.'))


urlpatterns = [
    re_path(r'^api/', api.urls),
    re_path(r'^api/.*$', api_404),
    re_path(r'', index, name='index'),
]


# ------------------------------
# api = HybridRouter(sort_urls=True, trailing_slash=False)
# api.register('budget/accounts', budget_api.AccountsViewSet, basename='account')
# api.register('budget/categories', budget_api.CategoriesViewSet, basename='category')
# api.register('budget/transactions', budget_api.TransactionsViewSet, basename='transaction')
# api.register('stocks/tickers', stocks_api.TickerViewSet, basename='ticker')
# api.add_url('^stocks/projection_trends$', stocks_apiviews.projection_trends, name='stocks/projection_trends')
