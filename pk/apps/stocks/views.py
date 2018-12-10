#!/usr/bin/env python
# encoding: utf-8
from rest_framework import viewsets
from rest_framework.response import Response
from .models import Stock, StockSerializer


class StocksViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.order_by('ticker')
    serializer_class = StockSerializer
    list_fields = ['id','url','ticker','close','mindate','maxdate','tags']

    def list(self, request, *args, **kwargs):
        queryset = Stock.objects.order_by('ticker')
        serializer = StockSerializer(queryset, context={'request':request},
            many=True, fields=self.list_fields)
        return Response({'data':serializer.data})
