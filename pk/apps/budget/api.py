# encoding: utf-8
import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from django.db.models import F, Q, Count, Sum, DecimalField
from django.db.models.functions import Cast
from pk import log, utils  # noqa
from pk.utils.api.serializers import DynamicFieldsSerializer, PartialFieldsSerializer
from pk.utils.api.viewsets import ModelViewSetWithAnnotations
from pk.utils.search import FIELDTYPES, SearchField, Search
from rest_framework import serializers, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .manager import TransactionManager
from .models import Account, Category, Transaction, KeyValue

DATEFORMAT = '%Y-%m-%d'
IGNORED = 'Ignored'
RESET_DECIMAL = Decimal('-99999.99')
RESET = ['_RESET', RESET_DECIMAL]
REVERSE = True   # Set 'True' or 'False' for reversed month order.
TRANSACTIONSEARCHFIELDS = {
    'bank': SearchField(FIELDTYPES.STR, 'account__name'),
    'date': SearchField(FIELDTYPES.DATE, 'date'),
    'payee': SearchField(FIELDTYPES.STR, 'payee'),
    'category': SearchField(FIELDTYPES.STR, 'category__name'),
    'amount': SearchField(FIELDTYPES.NUM, 'amount'),
    'approved': SearchField(FIELDTYPES.BOOL, 'approved'),
    'comment': SearchField(FIELDTYPES.STR, 'comment'),
}


class AccountSerializer(DynamicFieldsSerializer):
    class Meta:
        model = Account
        fields = ('id','url','name','fid','type','payee','balance','balancedt')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        account = Account(**validated_data)
        account.save()
        return account


class AccountsViewSet(ModelViewSetWithAnnotations):
    queryset = Account.objects.order_by('name')
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    list_fields = AccountSerializer.Meta.fields

    def annotations(self):
        return {'num_transactions': Count('transaction')}

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user).order_by('name')

    def list(self, request, *args, **kwargs):
        accounts = Account.objects.filter(user=request.user).order_by('name')
        page = self.paginate_queryset(accounts)
        serializer = AccountSerializer(page, context={'request':request}, many=True, fields=self.list_fields)
        response = self.get_paginated_response(serializer.data)
        utils.move_to_end(response.data, 'results')
        return self.append_metadata(response, accounts)


class CategorySerializer(DynamicFieldsSerializer):
    class Meta:
        model = Category
        fields = ('id','url','name','sortindex','budget','comment','exclude_budget')
    
    def to_internal_value(self, data):
        if data.get('budget'):
            data['budget'] = clean_amount(data['budget'])
        return super(CategorySerializer, self).to_internal_value(data)
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        account = Category(**validated_data)
        account.save()
        return account


class CategoriesViewSet(ModelViewSetWithAnnotations):
    queryset = Category.objects.order_by('-sortindex')
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    list_fields = CategorySerializer.Meta.fields

    def annotations(self):
        maxdate = datetime.date.today().replace(day=1)
        mindate = maxdate - relativedelta(years=1)
        return {
            'num_transactions': Count('transaction'),
            'year_transactions': Count('transaction', filter=Q(transaction__date__gte=mindate, transaction__date__lt=maxdate)),
            'year_total': Sum('transaction__amount', filter=Q(transaction__date__gte=mindate, transaction__date__lt=maxdate)),
            'year_average': Cast(F('year_total') / 12, DecimalField(max_digits=9, decimal_places=2))
        }
    
    def get_queryset(self):
        return Category.objects.filter(user=self.request.user).order_by('-sortindex')

    def list(self, request, *args, **kwargs):
        categories = self.get_queryset().order_by('sortindex')
        page = self.paginate_queryset(categories)
        serializer = CategorySerializer(page, context={'request':request}, many=True, fields=self.list_fields)
        response = self.get_paginated_response(serializer.data)
        utils.move_to_end(response.data, 'results')
        return self.append_metadata(response, categories)


class TransactionSerializer(DynamicFieldsSerializer):
    account = PartialFieldsSerializer(AccountSerializer, ('url','name'))
    category = PartialFieldsSerializer(CategorySerializer, ('url','name','budget'))

    class Meta:
        model = Transaction
        fields = ('id','url','trxid','date','payee','amount','approved',
            'comment','account','category')
    
    def to_internal_value(self, data):
        if data.get('amount') in RESET:
            data['amount'] = RESET_DECIMAL
        elif data.get('amount'):
            data['amount'] = clean_amount(data['amount'])
        return super(TransactionSerializer, self).to_internal_value(data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        user = self.context['request'].user
        # Update category_name
        category_name = self.context['request'].data.get('category_name')
        if category_name is not None:
            instance.category = None
            if category_name != '':
                instance.category = utils.get_object_or_none(Category, user=user, name__iexact=category_name)
                if not instance.category:
                    raise serializers.ValidationError("Unknown category '%s'." % category_name)
        # Some values can be reset
        if self.context['request'].data.get('date') in RESET: instance.date = instance.original_date
        if self.context['request'].data.get('payee') in RESET: instance.payee = instance.original_payee
        if self.context['request'].data.get('amount') in RESET: instance.amount = instance.original_amount
        instance.save()
        return instance


class TransactionsViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.order_by('-date')
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    list_fields = TransactionSerializer.Meta.fields

    def list(self, request, *args, **kwargs):
        searchdata = {}
        searchstr = request.GET.get('search')
        transactions = Transaction.objects.filter(user=request.user).order_by('-date', 'payee', 'id')
        if searchstr:
            search = Search(transactions, TRANSACTIONSEARCHFIELDS, searchstr)
            transactions = search.queryset()
            searchdata = {'searchstr':searchstr, 'errors':', '.join(search.errors),
                'datefilters':' AND '.join(search.datefilters)}
        page = self.paginate_queryset(transactions)
        serializer = TransactionSerializer(page, context={'request':request}, many=True, fields=self.list_fields)
        response = self.get_paginated_response(serializer.data)
        response.data.update(searchdata)
        response.data['unapproved'] = transactions.filter(approved=False).count()
        response.data['uncategorized'] = transactions.filter(category_id=None).count()
        utils.move_to_end(response.data, 'previous','next','upload','results')
        return response
    
    def summary():
        pass


class KeyValueSerializer(DynamicFieldsSerializer):
    class Meta:
        model = KeyValue
        fields = ('key','value','url')


class KeyValueViewSet(viewsets.ModelViewSet):
    queryset = KeyValue.objects.order_by('key')
    serializer_class = KeyValueSerializer
    permission_classes = [IsAuthenticated]
    list_fields = KeyValueSerializer.Meta.fields


def clean_amount(value):
    """ Clean a USD string such as -$99.99 to a Decimal value. """
    if isinstance(value, str):
        value = value.replace('$', '')
        value = value.replace(',', '')
        return Decimal(value)
    if isinstance(value, (int, float)):
        return Decimal(value)
    return value


@api_view(['get'])
def budget(request):
    root = reverse('api-root', request=request)
    return Response({
        'budget/accounts': f'{root}budget/accounts',
        'budget/categories': f'{root}budget/categories',
        'budget/keyvalue': f'{root}budget/keyvalue',
        'budget/summary': f'{root}budget/summary',
        'budget/transactions': f'{root}budget/transactions',
        'budget/upload': f'{root}budget/upload',
    })


@api_view(['get'])
@permission_classes([IsAuthenticated])
def summary(request, *args, **kwargs):
    # Create a tuple of ranges to iterate
    today = datetime.date.today()
    monthstart = datetime.date.today().replace(day=1)
    dateranges = (
        ('thismonth', today, today.replace(day=1)),
        ('lastmonth', monthstart, monthstart - relativedelta(months=1)),
        ('pastyear', monthstart, monthstart - relativedelta(years=1)),
    )
    # Create a dict of aggregates for the query
    result = {}
    aggs = {'num_transactions': Count('id')}
    for key, maxdate, mindate in dateranges:
        result[key] = {}
        result[key]['mindate'] = mindate.strftime(DATEFORMAT)
        result[key]['maxdate'] = maxdate.strftime(DATEFORMAT)
        aggs[f'{key}__transactions'] = Count('id', filter=Q(date__gte=mindate, date__lt=maxdate))
        aggs[f'{key}__income'] = Sum('amount', filter=Q(date__gte=mindate, date__lt=maxdate, amount__gt=0))
        aggs[f'{key}__spent'] = Sum('amount', filter=Q(date__gte=mindate, date__lt=maxdate, amount__lt=0))
        aggs[f'{key}__total'] = Sum('amount', filter=Q(date__gte=mindate, date__lt=maxdate))
    # Finish up
    transactions = Transaction.objects.filter(user=request.user, category__exclude_budget=False)
    transactions |= Transaction.objects.filter(user=request.user, category__isnull=True)
    qresult = transactions.aggregate(**aggs)
    for key, value in qresult.items():
        utils.rset(result, key, value, delim='__')
    result['pastyear']['average'] = round(Decimal(result['pastyear']['total'] / 12), 2)
    return Response(result)


@api_view(['put'])
@permission_classes([IsAuthenticated])
def upload(request, format=None):
    """ Upload new transactions to the budget app. """
    trxmanager = TransactionManager()
    for fileobj in request.FILES.values():
        trxmanager.import_qfx(request.user, fileobj.name, fileobj.file)
    return Response(trxmanager.get_status())
