# encoding: utf-8
from decimal import Decimal
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from pk.utils.decorators import current_user_or_superuser_required


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
