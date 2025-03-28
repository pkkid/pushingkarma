# encoding: utf-8
import logging
from django_searchquery import searchfields as sf
from django_searchquery.search import Search
from django.conf import settings
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_page
from ninja import Router
from ninja.decorators import decorate_view
from pk.utils import PageSchema, paginate, reverse
from typing import Optional
from .models import Ticker
from .schemas import TickerSchema
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
def list_tickers(request, search:Optional[str]='', page:Optional[int]=1):
    """ List tickers and basic information from the database.
        • search: Filter tickers by search string.
    """
    tickers = Ticker.objects.select_related('lastday').order_by('ticker')
    if search:
        searchobj = Search(TICKERSEARCHFIELDS)
        tickers = searchobj.get_queryset(tickers, search)
    data = paginate(request, tickers, page=page, perpage=10)
    for i in range(len(data['items'])):
        item = data['items'][i]
        itemdict = model_to_dict(item)
        itemdict['url'] = reverse(request, 'api:ticker', ticker=item.ticker)
        itemdict['lastday'] = model_to_dict(item.lastday)
        del itemdict['lastday']['ticker']
        data['items'][i] = itemdict
    return data


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
