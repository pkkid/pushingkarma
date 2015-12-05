#!/usr/bin/env python
# encoding: utf-8
"""
Pulled from django-rest-framework documentation
http://www.django-rest-framework.org/api-guide/serializers/#dynamically-modifying-fields
"""
from rest_framework import serializers


class DynamicFieldsSerializer(serializers.HyperlinkedModelSerializer):

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super(DynamicFieldsSerializer, self).__init__(*args, **kwargs)
        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)
