# encoding: utf-8
# Pulled from django-rest-framework documentation:
# http://www.django-rest-framework.org/api-guide/serializers/#dynamically-modifying-fields
from rest_framework import pagination, serializers


class CustomPageNumberPagination(pagination.PageNumberPagination):
    max_page_size = 9999                # Max page size
    page_size = 100                     # Default page size
    page_size_query_param = 'limit'     # Page size query paramter


class DynamicFieldsSerializer(serializers.HyperlinkedModelSerializer):

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
    _fields = fields or cls.Meta.fields

    class _PartialFieldsSerializer(cls):
        class Meta:
            model = cls.Meta.model
            fields = _fields
    
    return _PartialFieldsSerializer(**kwargs)
