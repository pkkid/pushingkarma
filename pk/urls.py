# encoding: utf-8
import logging
from django.shortcuts import redirect
from django.http import FileResponse
from django.conf import settings
from django.urls import re_path
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from http import HTTPStatus
from ninja import NinjaAPI
from ninja.errors import HttpError, ValidationError
from pk.apps.main.api import router as main_router
from pk.apps.budget.api import router as budget_router
from pk.apps.obsidian.api import router as obsidian_router
from pk.apps.reddit.api import router as reddit_router
from pk.apps.stocks.api import router as stocks_router
from pk.utils.ninja import root_router
from pk.utils.django import vue_devserver_running
log = logging.getLogger(__name__)

api = NinjaAPI(title='PushingKarma API', urls_namespace='api')
api.add_router('/', root_router)
api.add_router('/main', main_router)
api.add_router('/budget', budget_router)
api.add_router('/obsidian', obsidian_router)
api.add_router('/reddit', reddit_router)
api.add_router('/stocks', stocks_router)


@xframe_options_exempt
@ensure_csrf_cookie
def index(request):
    if url := vue_devserver_running(request):
        return redirect(url)
    filepath = f'{settings.BASE_DIR}/_dist/index.html'
    return FileResponse(open(filepath, 'rb'), content_type='text/html')


@api.exception_handler(Exception)
def api_exception(request, err):
    status = getattr(err, 'status_code', 500)
    phrase = HTTPStatus(status).phrase
    data = dict(status=phrase, message=str(err))
    if status == 500: log.exception(err)
    return api.create_response(request, data, status=status)


@api.exception_handler(ValidationError)
def api_validation_error(request, err):
    data = dict(status=422, message='Validation error')
    data['errors'] = {e['loc'][-1]:e['msg'] for e in err.errors}
    return api.create_response(request, data, status=422)


def api_404(request, err=None):
    return api_exception(request, HttpError(404, 'API endpoint not found.'))


urlpatterns = [
    re_path(r'^api/', api.urls),
    re_path(r'^api/.*$', api_404),
    re_path(r'', index, name='index'),
]
