#!/usr/bin/env python
# encoding: utf-8
from pk import utils
from pk.utils import context
from pk.utils.markdown import Markdown
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .models import Page, PageSerializer


def page(request, slug='root', tmpl='page.html'):
    page = utils.get_object_or_none(Page, slug=slug) or Page(slug=slug)
    data = context.core(request, menuitem='projects')
    data.page = PageSerializer(page, context={'request':request}).data
    return utils.response(request, tmpl, data)


def markdown(request):
    body = request.POST.get('body', '')
    md = Markdown(body, Page, '/p/')
    includes = sorted(md.meta['includes'].keys())
    return utils.response_json({'html':md.html, 'includes':includes})


class PagesViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.order_by('-created')
    serializer_class = PageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    list_fields = ['id','url','slug','created','modified']

    def list(self, request, *args, **kwargs):
        queryset = Page.objects.order_by('-created')
        serializer = PageSerializer(queryset, context={'request':request},
            many=True, fields=self.list_fields)
        return Response({'data':serializer.data})
