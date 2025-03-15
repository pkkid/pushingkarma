# encoding: utf-8
from django_searchquery import searchfields as sf
from pk import utils
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Ticker, TickerHistory

TICKERSEARCHFIELDS = [
    sf.StrField('ticker', 'ticker', desc='Ticker symbol', generic=True),
    sf.StrField('tags', 'tags', desc='User tags', generic=True),
]
    

class TickerSerializer(utils.DynamicFieldsSerializer):
    class Meta:
        model = Ticker
        fields = ('ticker', 'tags', 'info')


class TickerViewSet(utils.ViewSetMixin, viewsets.ModelViewSet):
    """ Rest endpoint to list or modifiy watched tickers. """
    serializer_class = TickerSerializer
    queryset = Ticker.objects.order_by('ticker')
    permission_classes = [IsAuthenticated]
    list_fields = TickerSerializer.Meta.fields

    def list(self, request, *args, **kwargs):
        return self.list_response(request, paginated=True, searchfields=TICKERSEARCHFIELDS)


class TickerHistorySerializer(utils.DynamicFieldsSerializer):
    class Meta:
        model = TickerHistory
        fields = ('ticker', 'date', 'close', 'high', 'low', 'volume')
