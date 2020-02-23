# encoding: utf-8
# Pulled from django-rest-framework documentation:
# http://www.django-rest-framework.org/api-guide/serializers/#dynamically-modifying-fields
from rest_framework import pagination, routers, serializers
from rest_framework.reverse import reverse


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


def PartialFieldsSerializer(cls, fields=None, **kwargs):
    """ Serializer allows only showing some of the fields on a model. """
    _fields = fields or cls.Meta.fields

    class _PartialFieldsSerializer(cls):
        class Meta:
            model = cls.Meta.model
            fields = _fields
    
    return _PartialFieldsSerializer(**kwargs)


class HybridRouter(routers.DefaultRouter):
    """ Hybriid router allowed both APIViews and class-based views.
        https://stackoverflow.com/a/37388298
    """
    def __init__(self, *args, **kwargs):
        super(HybridRouter, self).__init__(*args, **kwargs)
        self.view_urls = []

    def add_url(self, view):
        self.view_urls.append(view)

    def get_urls(self):
        return super(HybridRouter, self).get_urls() + self.view_urls

    def get_api_root_view(self, *args, **kwargs):
        original_view = super(HybridRouter, self).get_api_root_view()
        def view(request, *args, **kwargs):  # noqa
            resp = original_view(request, *args, **kwargs)
            namespace = request.resolver_match.namespace
            for view_url in self.view_urls:
                url_name = view_url.name
                if namespace:
                    url_name = namespace + ':' + url_name
                resp.data[view_url.name] = reverse(url_name, args=args, kwargs=kwargs,
                    request=request, format=kwargs.get('format', None))
            return resp
        return view