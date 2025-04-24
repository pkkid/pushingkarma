# encoding: utf-8
import logging
from datetime import timedelta
from django_searchquery import searchfields as sf
from django_searchquery.search import Search
from django.db.models import Max
from django.shortcuts import get_object_or_404
from ninja import Path, Query, Router
from pk.utils.ninja import PageSchema, paginate
from pk.utils.utils import percent
from .models import Ticker, TickerHistory
from .schemas import TickerSchema, DatasetsSchema
from . import utils as stock_utils
log = logging.getLogger(__name__)
router = Router()

TICKERSEARCHFIELDS = [
    sf.StrField('ticker', 'ticker', desc='Ticker symbol', generic=True),
    sf.StrField('tags', 'tags', desc='User tags', generic=True),
]


@router.get('/tickers/{pk}', response=TickerSchema, exclude_unset=True, url_name='ticker')
def get_ticker(request,
      pk: str=Path(None, description='Ticker symbol to get'),):
    """ List details for the specified ticker. """
    ticker = get_object_or_404(Ticker, pk=pk)
    return TickerSchema.from_orm(ticker)


@router.get('/tickers', response=PageSchema(TickerSchema), exclude_unset=True)
def list_tickers(request,
      search: str=Query('', description='Search term to filter tickers'),
      page: int=Query(1, description='Page number of results to return')):
    """ List tickers and basic information from the database. """
    tickers = Ticker.objects.select_related('lastday').order_by('ticker')
    if search:
        tickers = Search(TICKERSEARCHFIELDS).get_queryset(tickers, search)
    data = paginate(request, tickers, page=page, perpage=10)
    return data


@router.get('/chart_ranks', response=DatasetsSchema, exclude_unset=True)
def chart_ranks(request,
      periods: str=Query(None, description='Week periods to include in the chart (ie: 12w,10w,8w,6w,4w,2w)'),
      maxresults: int=Query(10, description='Maximum number of results to return (default: 10)'),
      search: str=Query('', description='Search term to filter tickers')):
    """ Return datasets to render a the Projected Ranks chart. """
    periods = (periods or '12w,10w,8w,6w,4w,2w').split(',')
    tickers = Ticker.objects.all()
    if search: tickers = Search(TICKERSEARCHFIELDS).get_queryset(tickers, search)
    if not len(tickers): return {'labels':[], 'datasets':[]}
    maxdate = TickerHistory.objects.filter(ticker__in=tickers).aggregate(Max('date'))['date__max']
    mindate = maxdate - timedelta(weeks=int(periods[0].rstrip('w'))+1)
    histories = stock_utils.histories_dict(tickers, mindate)
    # Pass 1: Calculate the percent change for each ticker
    datasets = {}
    for ticker in tickers:
        change = []
        history = histories[ticker.ticker]
        maxdate_close = stock_utils.value_for_date(history, maxdate, ticker.ticker)
        for period in periods:
            pdate = maxdate - timedelta(weeks=int(period.rstrip('w')))
            pdate_close = stock_utils.value_for_date(history, pdate, ticker.ticker)
            pdate_change = float(percent(maxdate_close, pdate_close) - 100)
            change.append(pdate_change)
        datasets[ticker.ticker] = {}
        datasets[ticker.ticker]['label'] = ticker.ticker
        datasets[ticker.ticker]['change'] = change
        datasets[ticker.ticker]['rank'] = []
    print(datasets[ticker.ticker]['change'])
    # Limit datasets to maxresults
    datasets = sorted(datasets.values(), key=lambda x: x['change'][-1], reverse=True)[:maxresults]
    # Pass 2: For each period, rank the tickers by the percent change
    for i, period in enumerate(periods):
        tickers = sorted(datasets, key=lambda x: x['change'][i], reverse=True)
        for rank, ticker in enumerate(tickers):
            ticker_rank = rank + 1
            ticker['rank'].append(ticker_rank)
    return {'labels':periods, 'datasets':datasets}
