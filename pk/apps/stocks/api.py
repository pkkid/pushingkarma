# encoding: utf-8
import logging
from datetime import timedelta
from django_searchquery import searchfields as sf
from django_searchquery.search import Search
from django.conf import settings
from django.db.models import Max
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_page
from ninja import Router
from ninja.decorators import decorate_view
from pk.utils import PageSchema, paginate, percent, reverse
from .models import Ticker, TickerHistory
from .schemas import TickerSchema, DatasetsSchema
from . import utils as stockutils
log = logging.getLogger(__name__)
router = Router()

TICKERSEARCHFIELDS = [
    sf.StrField('ticker', 'ticker', desc='Ticker symbol', generic=True),
    sf.StrField('tags', 'tags', desc='User tags', generic=True),
]


@router.get('/tickers/{ticker}', response=TickerSchema, exclude_unset=True, url_name='ticker')
@decorate_view(cache_page(0 if settings.DEBUG else 300))
def get_ticker(request, ticker:str):
    """ List details for the specified ticker. """
    data = model_to_dict(get_object_or_404(Ticker, ticker=ticker))
    data['url'] = reverse(request, 'api:ticker', ticker=data['ticker'])
    return data


@router.get('/tickers', response=PageSchema(TickerSchema), exclude_unset=True)
@decorate_view(cache_page(0 if settings.DEBUG else 300))
def list_tickers(request, search:str='', page:int=1):
    """ List tickers and basic information from the database.
        • search: Filter tickers by search string.
        • page: Page number of results to return
    """
    tickers = Ticker.objects.select_related('lastday').order_by('ticker')
    if search:
        tickers = Search(TICKERSEARCHFIELDS).get_queryset(tickers, search)
    data = paginate(request, tickers, page=page, perpage=10)
    for i in range(len(data['items'])):
        item = data['items'][i]
        itemdict = model_to_dict(item)
        itemdict['url'] = reverse(request, 'api:ticker', ticker=item.ticker)
        itemdict['lastday'] = model_to_dict(item.lastday)
        del itemdict['lastday']['ticker']
        data['items'][i] = itemdict
    return data


@router.get('/projected_ranks', response=DatasetsSchema, exclude_unset=True)
@decorate_view(cache_page(0 if settings.DEBUG else 300))
def get_projected_ranks(request, periods:str=None, maxresults:int=10, search:str=''):
    """ Return datasets to render a Projection Trends chart.
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
    histories = stockutils.histories_dict(tickers, mindate)
    # Pass 1: Calculate the percent change for each ticker
    datasets = {}
    for ticker in tickers:
        change = []
        history = histories[ticker.ticker]
        maxdate_close = stockutils.value_for_date(history, maxdate, ticker.ticker)
        for period in periods:
            pdate = maxdate - timedelta(weeks=int(period.rstrip('w')))
            pdate_close = stockutils.value_for_date(history, pdate, ticker.ticker)
            pdate_change = percent(maxdate_close, pdate_close) - 100
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
    return {'labels':periods, 'datasets':datasets}


# -------------------------------------
# from django_searchquery import searchfields as sf
# from pk import utils
# from rest_framework import viewsets
# from rest_framework.permissions import IsAuthenticated
# from .models import Ticker, TickerHistory

# class TickerHistorySerializer(utils.DynamicFieldsSerializer):
#     class Meta:
#         model = TickerHistory
#         fields = ('ticker', 'date', 'close', 'high', 'low', 'volume')


# class TickerSerializer(utils.DynamicFieldsSerializer):
#     lastday = utils.PartialFieldsSerializer(TickerHistorySerializer,
#         ('date', 'close', 'high', 'low', 'volume'))

#     class Meta:
#         model = Ticker
#         fields = ('ticker', 'tags', 'info', 'lastday')


# class TickerViewSet(utils.ViewSetMixin, viewsets.ModelViewSet):
#     """ Rest endpoint to list or modifiy watched tickers. """
#     serializer_class = TickerSerializer
#     permission_classes = [IsAuthenticated]
#     list_fields = TickerSerializer.Meta.fields

#     def get_queryset(self):
#         return Ticker.objects.select_related('lastday').order_by('ticker')

#     def list(self, request, *args, **kwargs):
#         return self.list_response(request, paginated=True, searchfields=TICKERSEARCHFIELDS)
