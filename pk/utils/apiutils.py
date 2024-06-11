# encoding: utf-8
from collections import OrderedDict
from decimal import Decimal
from django.urls import re_path
from pk.utils.decorators import current_user_or_superuser_required
from rest_framework import pagination, routers, serializers, viewsets
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.response import Response
from rest_framework.reverse import reverse
from pk import log


class CustomPageNumberPagination(pagination.PageNumberPagination):
    """ Returns a few more useful variables when paginating. """
    max_page_size = 9999                # Max page size
    page_size = 100                     # Default page size
    page_size_query_param = 'limit'     # Page size query paramter


class DynamicFieldsSerializer(serializers.HyperlinkedModelSerializer):
    """ Serializer allows dynamic fields.
        http://www.django-rest-framework.org/api-guide/serializers/#dynamically-modifying-fields
    """
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
    """ Hybrid router allowed both APIViews and class-based views.
        https://stackoverflow.com/a/37388298
    """
    def __init__(self, sort_urls=False, *args, **kwargs):
        super(HybridRouter, self).__init__(*args, **kwargs)
        self.sort_urls = sort_urls
        self.view_urls = []

    def add_url(self, regex, view, kwargs=None, name=None):
        django_url = re_path(regex, view, kwargs, name)
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


class ModelViewSetWithAnnotations(viewsets.ModelViewSet):
    # Annotations to include
    # Example: {'num_transactions': Count('transaction'), ...}
    annotations_key = 'meta'
    annotations = {}
    
    def append_metadata(self, response, queryset):
        """ Append data to a DRF response. """
        annotations = self.annotations()
        if not annotations: return response
        queryset = queryset.annotate(**annotations)
        itemids = {x['id']:x for x in queryset.values()}
        items = response.data['results'] if 'results' in response.data else [response.data]
        for item in items:
            itemdata = itemids[item['id']]
            item[self.annotations_key] = {}
            for key in annotations:
                value = itemdata[key]
                if isinstance(value, Decimal):
                    value = round(value, 2)
                item[self.annotations_key][key] = value
        return response

    def list(self, request, *args, **kwargs):
        response = super(ModelViewSetWithAnnotations, self).list(request, *args, **kwargs)
        return self.append_metadata(response, self.get_queryset())
    
    def create(self, request, *args, **kwargs):
        response = super(ModelViewSetWithAnnotations, self).create(request, *args, **kwargs)
        return self.append_metadata(response, self.get_queryset().filter(pk=response.data['id']))
    
    @current_user_or_superuser_required
    def retrieve(self, request, *args, **kwargs):
        response = super(ModelViewSetWithAnnotations, self).retrieve(request, *args, **kwargs)
        return self.append_metadata(response, self.get_queryset().filter(pk=kwargs['pk']))
    
    @current_user_or_superuser_required
    def update(self, request, *args, **kwargs):
        response = super(ModelViewSetWithAnnotations, self).update(request, *args, **kwargs)
        return self.append_metadata(response, self.get_queryset().filter(pk=kwargs['pk']))

    @current_user_or_superuser_required
    def partial_update(self, request, *args, **kwargs):
        response = super(ModelViewSetWithAnnotations, self).partial_update(request, *args, **kwargs)
        return self.append_metadata(response, self.get_queryset().filter(pk=kwargs['pk']))


class ModelViewSetWithUserPermissions(viewsets.ModelViewSet):
    """ This class assumes there is a `user` field on the model. """
    
    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied()
        return super(ModelViewSetWithUserPermissions, self).create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @current_user_or_superuser_required
    def retrieve(self, request, *args, **kwargs):
        return super(ModelViewSetWithUserPermissions, self).retrieve(request, *args, **kwargs)
    
    @current_user_or_superuser_required
    def update(self, request, *args, **kwargs):
        return super(ModelViewSetWithUserPermissions, self).update(request, *args, **kwargs)

    @current_user_or_superuser_required
    def partial_update(self, request, *args, **kwargs):
        return super(ModelViewSetWithUserPermissions, self).partial_update(request, *args, **kwargs)


def PartialFieldsSerializer(cls, fields=None, **kwargs):
    """ Serializer allows only showing some of the fields on a model. """
    _fields = fields or cls.Meta.fields

    class _PartialFieldsSerializer(cls):
        class Meta:
            model = cls.Meta.model
            fields = _fields
    
    return _PartialFieldsSerializer(**kwargs)


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
