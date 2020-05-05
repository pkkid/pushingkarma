# encoding: utf-8
from rest_framework import serializers


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


def PartialFieldsSerializer(cls, fields=None, **kwargs):
    """ Serializer allows only showing some of the fields on a model. """
    _fields = fields or cls.Meta.fields

    class _PartialFieldsSerializer(cls):
        class Meta:
            model = cls.Meta.model
            fields = _fields
    
    return _PartialFieldsSerializer(**kwargs)
