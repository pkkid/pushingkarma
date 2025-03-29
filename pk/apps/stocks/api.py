# encoding: utf-8
import logging
from datetime import timedelta
from django_searchquery import searchfields as sf
from django_searchquery.search import Search
from django.db.models import Max
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from ninja import Router
from pk.utils.django import reverse
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


@router.get('/tickers/{ticker}', response=TickerSchema, exclude_unset=True, url_name='ticker')
def get_ticker(request, ticker:str):
    """ List details for the specified ticker. """
    data = model_to_dict(get_object_or_404(Ticker, ticker=ticker))
    data['url'] = reverse(request, 'api:ticker', ticker=data['ticker'])
    return data


@router.get('/tickers', response=PageSchema(TickerSchema), exclude_unset=True)
def list_tickers(request, search:str='', page:int=1):
    """ List tickers and basic information from the database.
        • search: Filter tickers by search string.
        • page: Page number of results to return
    """
    tickers = Ticker.objects.select_related('lastday').order_by('ticker')
    if search: tickers = Search(TICKERSEARCHFIELDS).get_queryset(tickers, search)
    data = paginate(request, tickers, page=page, perpage=10)
    for i in range(len(data['items'])):
        item = data['items'][i]
        itemdict = model_to_dict(item)
        itemdict['url'] = reverse(request, 'api:ticker', ticker=item.ticker)
        itemdict['lastday'] = model_to_dict(item.lastday)
        del itemdict['lastday']['ticker']
        data['items'][i] = itemdict
    return data


@router.get('/chart_ranks', response=DatasetsSchema, exclude_unset=True)
def chart_ranks(request, periods:str=None, maxresults:int=10, search:str=''):
    """ Return datasets to render a the Projected Ranks chart.
        • periods: Week periods to include in the chart (ie: 12w,10w,8w,6w,4w,2w)
        • maxresults: Maximum number of results to return (default: 10).
        • search: Filter tickers by search string.
    """
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
