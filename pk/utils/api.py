# encoding: utf-8
# Pulled from django-rest-framework documentation:
# http://www.django-rest-framework.org/api-guide/serializers/#dynamically-modifying-fields
from collections import OrderedDict
from decimal import Decimal, getcontext
from django.conf.urls import url
from rest_framework import pagination, routers, serializers
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from pk import log


class CustomPageNumberPagination(pagination.PageNumberPagination):
    """ Returns a few more useful variables when paginating. """
    max_page_size = 9999                # Max page size
    page_size = 100                     # Default page size
    page_size_query_param = 'limit'     # Page size query paramter


class DynamicFieldsSerializer(serializers.HyperlinkedModelSerializer):
    """ Serializer allows dynamic fields. """
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super(DynamicFieldsSerializer, self).__init__(*args, **kwargs)
        if fields is not None:
            # Drop invalid fields
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class HybridRouter(routers.DefaultRouter):
    """ Hybriid router allowed both APIViews and class-based views.
        https://stackoverflow.com/a/37388298
    """
    def __init__(self, sort_urls=False, *args, **kwargs):
        super(HybridRouter, self).__init__(*args, **kwargs)
        self.sort_urls = sort_urls
        self.view_urls = []

    def add_url(self, regex, view, kwargs=None, name=None):
        django_url = url(regex, view, kwargs, name)
        self.view_urls.append(django_url)

    def get_urls(self):
        return super(HybridRouter, self).get_urls() + self.view_urls

    def get_api_root_view(self, *args, **kwargs):
        original_view = super(HybridRouter, self).get_api_root_view()
        def view(request, *args, **kwargs):  # noqa
            response = original_view(request, *args, **kwargs)
            namespace = request.resolver_match.namespace
            for view_url in self.view_urls:
                url_name = view_url.name
                url_name = f'{namespace}:{url_name}' if namespace else url_name
                response.data[view_url.name] = reverse(url_name, args=args,
                    kwargs=kwargs, request=request, format=kwargs.get('format', None))
                if self.sort_urls is True:
                    response.data = OrderedDict(sorted(response.data.items(), key=lambda x: x[0]))
            return response
        return view


def append_summary_data(response, queryset, **annotations):
    """ Append data to a DRF list response. """
    queryset = queryset.annotate(**annotations)
    itemids = {x['id']:x for x in queryset.values()}
    for item in response.data['results']:
        itemdata = itemids[item['id']]
        item['summary'] = {}
        for key in annotations:
            value = itemdata[key]
            if isinstance(value, Decimal):
                value = round(value, 2)
            item['summary'][key] = value
    return response


def custom_exception_handler(err, context):
    """ Custom exception handler for Django Rest Framework.
        https://www.django-rest-framework.org/api-guide/exceptions/
    """
    IGNORE_ERRORS = (NotAuthenticated,)
    if isinstance(err, IGNORE_ERRORS):
        log.warning(err)
        return Response({'detail':str(err)})
    log.exception(err)
    return Response({'detail':str(err)})


def PartialFieldsSerializer(cls, fields=None, **kwargs):
    """ Serializer allows only showing some of the fields on a model. """
    _fields = fields or cls.Meta.fields

    class _PartialFieldsSerializer(cls):
        class Meta:
            model = cls.Meta.model
            fields = _fields
    
    return _PartialFieldsSerializer(**kwargs)
