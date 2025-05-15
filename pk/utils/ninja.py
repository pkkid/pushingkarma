# encoding: utf-8
import logging
from django.conf import settings
from django.core.paginator import Paginator
from ninja import Router
from ninja import Schema
from pydantic import create_model
from typing import List, Type
from urllib.parse import urlencode
log = logging.getLogger(__name__)
root_router = Router()

ROOT_DESCRIPTION = """
    Returns a list of all available endpoints in the API.<br/>
    • Root endpoint: <a href='{domain}/api/'>{domain}/api/</a><br/>
    • OpenAPI Spec: <a href='{domain}/api/openapi.json'>{domain}/api/openapi.json</a><br/>
    • Swagger Docs: <a href='{domain}/api/docs'>{domain}/api/docs</a>
""".format(domain=settings.DOMAIN)


@root_router.get('/', description=ROOT_DESCRIPTION)
def api_root(request):
    """ Returns a list of all available endpoints in the API. """
    return root_router.api.get_openapi_schema()


def PageSchema(itemschema:Type[Schema]):
    """ Factory to create a PageSchema with items of type itemsschema. """
    modelname = itemschema.__name__.replace('Schema', '')
    return create_model(f'{modelname}PageSchema',
        count = (int, ...),
        previous = (str, None),
        next = (str, None),
        items = (List[itemschema], ...),
    )


def paginate(request, items, page=1, perpage=100):
    """ Paginate a queryset and return the results for the specified page. """
    paginator = Paginator(items, perpage)
    pageobj = paginator.page(page)
    return {k:v for k,v in dict(
        count = paginator.count,
        previous = _pageurl(request, pageobj.previous_page_number()) if pageobj.has_previous() else None,
        next = _pageurl(request, pageobj.next_page_number()) if pageobj.has_next() else None,
        items = list(pageobj.object_list),
    ).items() if v is not None}


def _pageurl(request, pagenum):
    """ Create URL for the specified page number. """
    query_params = request.GET.copy()
    query_params['page'] = pagenum
    url = f'{settings.DOMAIN}{request.path}'
    if query_params: url += f'?{urlencode(query_params)}'
    return url
