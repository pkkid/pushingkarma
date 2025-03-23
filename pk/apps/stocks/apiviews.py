# encoding: utf-8
from datetime import timedelta
from django_searchquery.search import Search
from django.db.models import Max
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from pk import utils
from .models import Ticker, TickerHistory
from . import api, utils as sutils

@api_view(['get'])
@permission_classes([IsAuthenticated])
def projection_trends(request):
    """ Return datasets to render a Projection Trends chart.
        • periods: Week periods to include in the chart (ie: 12w,10w,8w,6w,4w,2w)
        • maxresults: Maximum number of results to return (default: 10).
        • search: Filter tickers by search string.
    """
    # import time; time.sleep(5)
    periods = request.query_params.get('periods', '12w,10w,8w,6w,4w,2w').split(',')
    maxresults = int(request.query_params.get('maxresults', 10))
    searchstr = request.GET.get('search', '')
    tickers = Search(api.TICKERSEARCHFIELDS).get_queryset(Ticker.objects.all(), searchstr)
    if not len(tickers): return Response({'labels':[], 'datasets':[]})
    maxdate = TickerHistory.objects.filter(ticker__in=tickers).aggregate(Max('date'))['date__max']
    mindate = maxdate - timedelta(weeks=int(periods[0].rstrip('w'))+1)
    histories = sutils.histories_dict(tickers, mindate)
    # Pass 1: Calculate the percent change for each ticker
    datasets = {}
    for ticker in tickers:
        change = []
        history = histories[ticker.ticker]
        maxdate_close = sutils.value_for_date(history, maxdate, ticker.ticker)
        for period in periods:
            pdate = maxdate - timedelta(weeks=int(period.rstrip('w')))
            pdate_close = sutils.value_for_date(history, pdate, ticker.ticker)
            pdate_change = utils.percent(maxdate_close, pdate_close) - 100
            change.append(pdate_change)
        datasets[ticker.ticker] = {}
        datasets[ticker.ticker]['label'] = ticker.ticker
        datasets[ticker.ticker]['change'] = change
        datasets[ticker.ticker]['rank'] = []
    # Limit datasets to maxresults
    datasets = sorted(datasets.values(), key=lambda x: x['change'][-1], reverse=True)[:maxresults]
    # Pass 2: For each period, rank the tickers by the percent change
    for i, period in enumerate(periods):
        tickers = sorted(datasets, key=lambda x: x['change'][i], reverse=True)
        for rank, ticker in enumerate(tickers):
            ticker_rank = rank + 1
            ticker['rank'].append(ticker_rank)
    return Response({'labels':periods, 'datasets':datasets})
