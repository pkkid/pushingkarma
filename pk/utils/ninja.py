# encoding: utf-8
import base64
import json
import logging
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q
from ninja import Router
from ninja import Schema
from pydantic import create_model
from typing import List, Type, Optional
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
        next_cursor = (Optional[str], None),  # Cursor for keyset pagination
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


def paginate_cursor(request, queryset, cursor=None, perpage=100, sort_fields=None):
    """ Paginate a queryset using keyset/cursor pagination.
        request: Django request object
        queryset: QuerySet to paginate
        cursor: Base64-encoded cursor string from previous response (or None for first page)
        perpage: Number of items to return
        sort_fields: List of (field_name, direction) tuples where direction is '>' or '<'
            Example: [('date', '<'), ('payee', '>'), ('id', '>')]
            This represents: date DESC, payee ASC, id ASC
        Returns: Dict with 'items', 'next_cursor', and 'count' keys
    """
    if not sort_fields:
        raise ValueError('sort_fields is required for cursor pagination')
    total_count = queryset.count()
    cursor_data = _decode_cursor(cursor)
    queryset = _build_cursor_queryset(queryset, cursor_data, sort_fields)
    items = list(queryset[:perpage + 1])
    has_more = len(items) > perpage
    items = items[:perpage]
    result = {'items':items, 'count':total_count}
    if has_more and items:
        result['next_cursor'] = _encode_cursor(items[-1], sort_fields)
    return result


def _build_cursor_queryset(queryset, cursor_data, sort_fields):
    """ Apply keyset/cursor filtering to the queryset. """
    if not cursor_data:
        return queryset
    qobj = Q()
    for i, (field, direction) in enumerate(sort_fields):
        condition_q = Q()
        for j in range(i):
            prev_field, _ = sort_fields[j]
            prev_value = cursor_data.get(prev_field)
            if prev_value is not None:
                condition_q &= Q(**{prev_field: prev_value})
        cursor_value = cursor_data.get(field)
        if cursor_value is None:
            continue
        lookup = 'gt' if direction == '>' else 'lt'
        condition_q &= Q(**{f'{field}__{lookup}': cursor_value})
        qobj |= condition_q
    if not qobj:
        return queryset
    return queryset.filter(qobj)


def _decode_cursor(cursor):
    """ Decode a base64 cursor string into a dictionary. """
    if not cursor:
        return None
    try:
        cursor_json = base64.b64decode(cursor).decode('utf-8')
        return json.loads(cursor_json)
    except Exception as exc:
        log.warning(f'Failed to decode cursor: {exc}')
        return None


def _encode_cursor(item, sort_fields):
    """ Encode cursor values from the given item and sort fields. """
    cursor_dict = {}
    for field, _ in sort_fields:
        value = getattr(item, field, None)
        cursor_dict[field] = str(value) if value is not None else None
    cursor_json = json.dumps(cursor_dict, separators=(',', ':'), default=str)
    return base64.b64encode(cursor_json.encode('utf-8')).decode('utf-8')


def _pageurl(request, pagenum):
    """ Create URL for the specified page number. """
    query_params = request.GET.copy()
    query_params['page'] = pagenum
    # Keep pagination URLs on the same origin as the current request.
    # Using settings.DOMAIN can point to a different host in development,
    # which drops session cookies on follow-up page requests.
    url = request.path
    if query_params: url += f'?{urlencode(query_params)}'
    return url
