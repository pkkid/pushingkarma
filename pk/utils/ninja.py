# encoding: utf-8
from collections import defaultdict
from django.core.paginator import Paginator
from ninja import Router
from ninja import Schema
from pydantic import create_model
from typing import List, Type
from urllib.parse import urlencode
root_router = Router()


@root_router.get('/')
def api_root(request):
    """ Returns a list of all available endpoints in the API. """
    baseurl = f'{request.scheme}://{request.get_host()}'
    response = {'documentation':{
        'swagger': f'{baseurl}/api/docs',
        'openapi': f'{baseurl}/api/openapi.json'
    }}
    schema = root_router.api.get_openapi_schema()
    paths = schema.get('paths', {})
    endpoints = defaultdict(list)
    for path, methods in paths.items():
        category = path.split('/')[2] or 'root'
        for method, details in methods.items():
            endpoints[category].append({
                'method': method.upper(),
                'summary': details.get('summary', ''),
                'description': details.get('description', '').strip(),
                'path': f'{baseurl}{path}',
                'category': category,
                'parameters': summarize_params(details, schema),
            })
    response['endpoints'] = endpoints
    return response


def summarize_params(details, fullschema):
    params = {}
    # Extract path and query parameters
    for param in details.get('parameters', []):
        params[param.get('name')] = dict(
            type = param.get('schema',{})['type'],
            description = param.get('description', '').strip(),
            required = param.get('required', False),
            location = param.get('in')
        )
    # Extract request body schema if available
    if 'requestBody' in details:
        content = details.get('requestBody', {}).get('content', {})
        if 'application/json' in content:
            schema = content.get('application/json', {}).get('schema', {})
            if '$ref' in schema:
                refpath = schema['$ref']
                schemaname = refpath.split('/')[-1]
                schema = fullschema.get('components', {}).get('schemas', {}).get(schemaname, {})
            properties = schema.get('properties', {})
            reqfields = schema.get('required', [])
            for fname, fprops in properties.items():
                params[fname] = dict(
                    type = fprops.get('anyOf',[{}])[0].get('type', fprops.get('type', 'object')),
                    description = fprops.get('description', '').strip(),
                    required = fname in reqfields,
                    location = 'body'
                )
    return params


def PageSchema(itemschema:Type[Schema]):
    """ Factory to create a PageSchema with items of type itemsschema. """
    return create_model('PageSchema',
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
    url = f'{request.scheme}://{request.get_host()}{request.path}'
    if query_params: url += f'?{urlencode(query_params)}'
    return url
