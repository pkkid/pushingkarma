# encoding: utf-8
from collections import OrderedDict
from django.urls import re_path
from rest_framework import routers
from rest_framework.reverse import reverse


class HybridRouter(routers.DefaultRouter):
    """ Hybriid router allowed both APIViews and class-based views.
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
