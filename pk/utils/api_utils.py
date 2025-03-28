# encoding: utf-8
from collections import defaultdict
from ninja import Router
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
        category = path.split('/')[2]
        # if not category: continue
        # print(category)
        for method, details in methods.items():
            endpoints[category].append({
                'method': method.upper(),
                'summary': details.get('summary', ''),
                'description': details.get('description', '').strip(),
                'path': f'{baseurl}{path}',
            })
    response['endpoints'] = endpoints
    return response


# ------------------------------
# # encoding: utf-8
# import logging
# from django_searchquery.search import Search
# from django.core.exceptions import NON_FIELD_ERRORS as DJANGO_NON_FIELD_ERRORS
# from django.core.exceptions import ValidationError as DjangoValidationError
# from django.db.models.query import QuerySet
# from django.urls import re_path
# from pk import utils
# from rest_framework import pagination, routers, serializers
# from rest_framework.exceptions import ValidationError as RestValidationError
# from rest_framework.response import Response
# from rest_framework.reverse import reverse
# from rest_framework.views import api_settings
# from rest_framework.views import exception_handler as rest_exception_handler
# log = logging.getLogger(__name__)

# REST_NON_FIELD_ERRORS = api_settings.NON_FIELD_ERRORS_KEY


# def api_exception_handler(exc, context):
#     """ Custom exception handler for Django Rest Framework.
#         https://djangotherightway.com/convert-django-validation-errors-to-drf-compatible-errors
#     """
#     if isinstance(exc, DjangoValidationError):
#         data = exc.message_dict
#         if DJANGO_NON_FIELD_ERRORS in data:
#             data[REST_NON_FIELD_ERRORS] = data[DJANGO_NON_FIELD_ERRORS]
#             del data[DJANGO_NON_FIELD_ERRORS]
#         exc = RestValidationError(detail=data)
#     return rest_exception_handler(exc, context)


# class CustomPageNumberPagination(pagination.PageNumberPagination):
#     """ Returns a few more useful variables when paginating. """
#     max_page_size = 9999                # Max page size
#     page_size = 100                     # Default page size
#     page_size_query_param = 'limit'     # Page size query paramter


# class DynamicFieldsSerializer(serializers.HyperlinkedModelSerializer):
#     """ Serializer allows dynamic fields.
#         http://www.django-rest-framework.org/api-guide/serializers/#dynamically-modifying-fields
#     """
#     def __init__(self, *args, **kwargs):
#         fields = kwargs.pop('fields', None)
#         super(DynamicFieldsSerializer, self).__init__(*args, **kwargs)
#         if fields is not None:
#             # Drop invalid fields
#             allowed = set(fields)
#             existing = set(self.fields.keys())
#             for field_name in existing - allowed:
#                 self.fields.pop(field_name)


# class HybridRouter(routers.DefaultRouter):
#     """ Hybrid router allowed both APIViews and class-based views.
#         https://stackoverflow.com/a/37388298
#     """
#     def __init__(self, sort_urls=False, *args, **kwargs):
#         super(HybridRouter, self).__init__(*args, **kwargs)
#         self.sort_urls = sort_urls
#         self.view_urls = []

#     def add_url(self, regex, view, kwargs=None, name=None):
#         django_url = re_path(regex, view, kwargs, name)
#         self.view_urls.append(django_url)

#     def get_urls(self):
#         return super(HybridRouter, self).get_urls() + self.view_urls

#     def get_api_root_view(self, *args, **kwargs):
#         original_view = super(HybridRouter, self).get_api_root_view()
#         def view(request, *args, **kwargs):  # noqa
#             response = original_view(request, *args, **kwargs)
#             namespace = request.resolver_match.namespace
#             for view_url in self.view_urls:
#                 url_name = view_url.name
#                 url_name = f'{namespace}:{url_name}' if namespace else url_name
#                 response.data[view_url.name] = reverse(url_name, args=args,
#                     kwargs=kwargs, request=request, format=kwargs.get('format', None))
#                 if self.sort_urls is True:
#                     response.data = dict(sorted(response.data.items(), key=lambda x: x[0]))
#             return response
#         return view


# def PartialFieldsSerializer(cls, fields, *args, **kwargs):
#     """ Serializer allows only showing some of the fields on a model. """
#     _fields = fields or cls.Meta.fields

#     class _PartialFieldsSerializer(cls):
#         class Meta:
#             model = cls.Meta.model
#             fields = _fields
    
#     return _PartialFieldsSerializer(*args, **kwargs)


# class ViewSetMixin():
#     """ Mixin provides useful utility functions to a viewset. """

#     def retrieve(self, request, *args, **kwargs):
#         """ Appends additional (more resource intensive) details to the result if requested. """
#         instance = self.get_object()
#         response = self.add_requested_details(instance, request)
#         self._reorder_keys(response.data)
#         return response

#     def add_requested_details(self, instance, request, data=None):
#         """ Convenience function to read the details GET argument and append
#             additional information to the response.
#         """
#         data = data or self.get_serializer(instance).data
#         details = filter(None, request.query_params.get('details', '').split(','))
#         for detail in details:
#             funcname = f'get_{detail}_details'
#             if func := getattr(self, funcname, None):
#                 data[detail] = func(request, instance)
#                 continue
#             log.warning(f"Details function not defined '{funcname}'")
#         return Response(data)
    
#     def list_response(self, request, paginated=False, searchfields=None, queryset=None):
#         """ Search and list results with pagination and/or search. This is kind of
#             a kitchen sink response function, but it works well.
#         """
#         if queryset is None:
#             queryset = self.get_queryset()
#         # Run the queryset through django_searchquery.Search if searchfields specified.
#         # Reads the search GET parameter and filters the queryset accordingly.
#         if searchfields:
#             searchstr = request.GET.get('search')
#             search = Search(searchfields)
#             queryset = search.get_queryset(queryset, searchstr)
#         # Use the paginated serializer if requested.
#         # Otherwise all results returned by default.
#         context = {'request':request, 'view':'list'}
#         if paginated:
#             page = self.paginate_queryset(queryset)
#             serializer = self.serializer_class(page, fields=self.list_fields, context=context, many=True)
#             response = self.get_paginated_response(serializer.data)
#         else:
#             serializer = self.serializer_class(queryset, context=context, many=True)
#             data = {'count':len(serializer.data), 'results': serializer.data}
#             response = Response(data)
#         # Append additional search data to the response
#         # Search meta contains search fields and any errors
#         # Search.query is the raw SQL Query to fetch results
#         if searchfields:
#             response.data['search'] = search.meta
#             response.data['search']['query'] = utils.queryset_str(queryset)
#         # Check we want to append any metadata about the list results
#         if getattr(self, 'list_meta', None):
#             response.data['meta'] = self.list_meta(request, queryset)
#         # Reorder the keys and return
#         self._reorder_keys(response.data)
#         return response
    
#     def _reorder_keys(self, data):
#         if 'previous' in data.keys():
#             utils.toback(data, 'previous')
#         if 'next' in data.keys():
#             utils.toback(data, 'next')
#         for key in list(data.keys()):
#             if isinstance(data[key], dict):
#                 utils.toback(data, key)
#         for key in list(data.keys()):
#             if isinstance(data[key], (list, QuerySet)):
#                 utils.toback(data, key)
#         return data
