# encoding: utf-8
from decimal import Decimal
from rest_framework import viewsets


class ModelViewSetWithAnnotations(viewsets.ModelViewSet):
    # Annotations to include
    # Example: {'num_transactions': Count('transaction'), ...}
    annotations_key = 'meta'
    annotations = {}
    
    def append_metadata(self, response, queryset):
        """ Append data to a DRF response. """
        if not self.annotations: return response
        queryset = queryset.annotate(**self.annotations)
        itemids = {x['id']:x for x in queryset.values()}
        items = response.data['results'] if 'results' in response.data else [response.data]
        for item in items:
            itemdata = itemids[item['id']]
            item[self.annotations_key] = {}
            for key in self.annotations:
                value = itemdata[key]
                if isinstance(value, Decimal):
                    value = round(value, 2)
                item[self.annotations_key][key] = value
        return response

    def list(self, request, *args, **kwargs):
        response = super(ModelViewSetWithAnnotations, self).create(request, *args, **kwargs)
        return self.append_metadata(response, self.queryset)
    
    def create(self, request, *args, **kwargs):
        response = super(ModelViewSetWithAnnotations, self).create(request, *args, **kwargs)
        return self.append_metadata(response, self.queryset.filter(pk=response.data['id']))
    
    def retrieve(self, request, *args, **kwargs):
        response = super(ModelViewSetWithAnnotations, self).retrieve(request, *args, **kwargs)
        return self.append_metadata(response, self.queryset.filter(pk=kwargs['pk']))
    
    def update(self, request, *args, **kwargs):
        response = super(ModelViewSetWithAnnotations, self).update(request, *args, **kwargs)
        return self.append_metadata(response, self.queryset.filter(pk=kwargs['pk']))

    def partial_update(self, request, *args, **kwargs):
        response = super(ModelViewSetWithAnnotations, self).partial_update(request, *args, **kwargs)
        return self.append_metadata(response, self.queryset.filter(pk=kwargs['pk']))
