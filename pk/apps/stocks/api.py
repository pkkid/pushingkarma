# encoding: utf-8
from datetime import datetime, timedelta
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
    serializer_class = TickerSerializer
    queryset = Ticker.objects.order_by('ticker')
    permission_classes = [IsAuthenticated]
    list_fields = TickerSerializer.Meta.fields

    def list(self, request, *args, **kwargs):
        return self.list_response(request, paginated=True, searchfields=TICKERSEARCHFIELDS)
    
    def get_history_details(self, obj):
        """ Returns the number of linked bugs. """
        mindate = datetime.now() - timedelta(days=366)
        history = obj.history.filter(date__gte=mindate).values('date', 'close').order_by('date')
        history = {h['date'].strftime('%Y-%m-%d'): h['close'] for h in history}
        return history


class TickerHistorySerializer(utils.DynamicFieldsSerializer):
    class Meta:
        model = TickerHistory
        fields = ('ticker', 'date', 'close', 'high', 'low', 'volume')
