# encoding: utf-8
import csv as pycsv
from datetime import datetime, timedelta
from django.http import HttpResponse, HttpResponseBadRequest
from pk.utils.api.serializers import DynamicFieldsSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.reverse import reverse
from .models import ADJCLOSE, Stock


class StockSerializer(DynamicFieldsSerializer):
    class Meta:
        model = Stock
        fields = ('id','url','ticker','description','close',
            'mindate','maxdate','modified','tags','history')


class StocksViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.order_by('ticker')
    serializer_class = StockSerializer
    list_fields = ['id','url','ticker','description',
        'close','mindate','maxdate','tags']

    def list(self, request, *args, **kwargs):
        queryset, _ = _get_stocks(request)
        queryset = queryset or Stock.objects.order_by('ticker')
        serializer = StockSerializer(queryset, context={'request':request},
            many=True, fields=self.list_fields)
        return Response({'data':serializer.data})


@api_view(['get'])
def stocks(request):
    root = reverse('api-root', request=request)
    return Response({
        'stocks/csv': f'{root}stocks/csv',
        'stocks/list': f'{root}stocks/list',
    })


@api_view(['get'])
@permission_classes([AllowAny])
def csv(request, *args, **kwargs):
    # Get the list of stocks to return
    stocks, title = _get_stocks(request)
    stocks = [s for s in stocks if s.data != '{}']
    if not stocks:
        return HttpResponseBadRequest(content='No tickers specified')
    # Find the min date to to return
    years = request.GET.get('years', 3)
    yearsago = (datetime.now() - timedelta(days=366*years)).strftime('%Y-%m-%d')
    oldest = sorted(stocks, key=lambda x:x.mindate)[0]
    # Build the csv response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="stocks.csv"'
    writer = pycsv.writer(response)
    writer.writerow([title] + [s.ticker.replace('.','') for s in stocks])
    writer.writerow([''] + [s.description for s in stocks])
    for datestr in oldest.history.keys():
        writer.writerow([datestr] + [_get_value(datestr, s) for s in stocks])
        if datestr < yearsago:
            break
    return response


def _get_stocks(request):
    stocks, title = None, None
    if 'ticker' in request.GET:
        tickers = [request.GET.get('ticker','')]
        stocks = Stock.objects.filter(ticker__in=tickers).order_by('ticker')
        title = ', '.join(tickers)
    elif 'tickers' in request.GET:
        tickers = request.GET.get('tickers','').split(',')
        stocks = Stock.objects.filter(ticker__in=tickers).order_by('ticker')
        title = ', '.join(tickers)
    elif 'tag' in request.GET:
        tag = request.GET.get('tag','').lower()
        stocks = Stock.objects.filter(tags__icontains=tag).order_by('ticker')
        title = tag
    return stocks, title


def _get_value(datestr, stock):
    """ The data from Alphavantage is messy. This function handles a few things.
        1. If a value is missing, we grab the previous value.
    """
    value = stock.history.get(datestr,{}).get(ADJCLOSE,'')
    if not value:
        keys = sorted([key for key in stock.keys if key < datestr], reverse=True)
        prev = stock.history[keys[0]].get(ADJCLOSE) if len(keys) >= 1 else None
        return prev
    return value
