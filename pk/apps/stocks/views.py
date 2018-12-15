#!/usr/bin/env python
# encoding: utf-8
import csv
from datetime import datetime, timedelta
from django.http import HttpResponse, HttpResponseBadRequest
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import list_route
from .models import ADJCLOSE, Stock, StockSerializer


class StocksViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.order_by('ticker')
    serializer_class = StockSerializer
    list_fields = ['id','url','ticker','description',
        'close','mindate','maxdate','tags']

    def list(self, request, *args, **kwargs):
        queryset = Stock.objects.order_by('ticker')
        serializer = StockSerializer(queryset, context={'request':request},
            many=True, fields=self.list_fields)
        return Response({'data':serializer.data})

    @list_route(methods=['get'])
    def csv(self, request, *args, **kwargs):
        # Get the list of stocks to return
        if 'ticker' in request.GET:
            tickers = [request.GET.get('ticker','')]
            stocks = Stock.objects.filter(ticker__in=tickers).order_by('ticker')
        elif 'tickers' in request.GET:
            tickers = request.GET.get('tickers','').split(',')
            stocks = Stock.objects.filter(ticker__in=tickers).order_by('ticker')
        elif 'tag' in request.GET:
            tag = request.GET.get('tag','').lower()
            stocks = Stock.objects.filter(tags__icontains=tag).order_by('ticker')
        years = request.GET.get('years', 4)
        # Verify we have stocks to return and get the oldest date
        if not stocks:
            return HttpResponseBadRequest(content='No tickers specified')
        oldest = sorted(stocks, key=lambda x:x.mindate)[0]
        yearsago = (datetime.now() - timedelta(days=366*years)).strftime('%Y-%m-%d')
        # Build the csv response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="stocks.csv"'
        writer = csv.writer(response)
        writer.writerow([''] + [s.ticker.replace('.','') for s in stocks])
        writer.writerow([''] + [s.description for s in stocks])
        for datestr in oldest.history.keys():
            row = [datestr]
            for stock in stocks:
                value = stock.history.get(datestr,{}).get(ADJCLOSE,'')
                if not value:
                    value = self._look_ahead(datestr, stock)
                row.append(value)
            writer.writerow(row)
            if datestr < yearsago:
                break
        return response

    def _look_ahead(self, datestr, stock):
        keys = stock.history.keys()
        keys = sorted([key for key in keys if key > datestr])
        nextkey = keys[0] if keys else None
        return stock.history.get(nextkey,{}).get(ADJCLOSE,'')
