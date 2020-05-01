# encoding: utf-8
from decimal import Decimal
from django.conf import settings
from django.db.models import Count, Min, Max
from pk import log, utils
from pk.utils.api import DynamicFieldsSerializer, PartialFieldsSerializer
from pk.utils.search import FIELDTYPES, SearchField, Search
from rest_framework import serializers, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .manager import TransactionManager
from .models import Account, Category, Transaction, KeyValue, UNCATEGORIZED

ACCOUNTS = settings.BUDGET_ACCOUNTS
CATEGORY_NULL = {'id':'null', 'name':UNCATEGORIZED, 'url':None, 'sortindex':999, 'budget':'0.00', 'comment':''}
DATEFORMAT = '%Y-%m-%d'
IGNORED = 'Ignored'
REVERSE = True   # Set 'True' or 'False' for reversed month order.
TRANSACTIONSEARCHFIELDS = {
    'bank': SearchField(FIELDTYPES.STR, 'account__name'),
    'date': SearchField(FIELDTYPES.DATE, 'date'),
    'payee': SearchField(FIELDTYPES.STR, 'payee'),
    'category': SearchField(FIELDTYPES.STR, 'category__name'),
    'amount': SearchField(FIELDTYPES.NUM, 'amount'),
    'approved': SearchField(FIELDTYPES.BOOL, 'approved'),
    'comment': SearchField(FIELDTYPES.STR, 'comment'),
    'memo': SearchField(FIELDTYPES.STR, 'memo'),
}


class AccountSerializer(DynamicFieldsSerializer):
    first_transaction = serializers.DateField()
    last_transaction = serializers.DateField()
    num_transactions = serializers.IntegerField()

    class Meta:
        model = Account
        fields = ('id', 'url', 'name', 'fid', 'type', 'payee', 'balance', 'balancedt',
            'first_transaction', 'last_transaction', 'num_transactions')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        account = Account(**validated_data)
        account.save()
        return account


class AccountsViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.order_by('name')
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    list_fields = AccountSerializer.Meta.fields

    def list(self, request, *args, **kwargs):
        accounts = Account.objects.filter(user=request.user).order_by('name')
        accounts = accounts.annotate(
            first_transaction=Min('transaction__date'),
            last_transaction=Max('transaction__date'),
            num_transactions=Count('transaction'))
        page = self.paginate_queryset(accounts)
        serializer = AccountSerializer(page, context={'request':request}, many=True, fields=self.list_fields)
        response = self.get_paginated_response(serializer.data)
        utils.move_to_end(response.data, 'results')
        return response


class CategorySerializer(DynamicFieldsSerializer):
    class Meta:
        model = Category
        fields = ('id', 'url', 'name', 'sortindex', 'budget', 'comment',
            'exclude_budget', 'exclude_totals')
    
    def to_internal_value(self, data):
        budget = data.get('budget')
        if budget:
            budget = budget.replace('$', '')
            budget = budget.replace(',', '')
            data['budget'] = Decimal(budget)
        return super(CategorySerializer, self).to_internal_value(data)
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        account = Category(**validated_data)
        account.save()
        return account


class CategoriesViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.order_by('-sortindex')
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    list_fields = CategorySerializer.Meta.fields

    def list(self, request, *args, **kwargs):
        categories = Category.objects.filter(user=request.user).order_by('sortindex')
        page = self.paginate_queryset(categories)
        serializer = CategorySerializer(page, context={'request':request}, many=True, fields=self.list_fields)
        response = self.get_paginated_response(serializer.data)
        utils.move_to_end(response.data, 'results')
        return response


class TransactionSerializer(DynamicFieldsSerializer):
    account = PartialFieldsSerializer(AccountSerializer, ('url','name'))
    category = PartialFieldsSerializer(CategorySerializer, ('url','name','budget'))

    class Meta:
        model = Transaction
        fields = ('id','url','trxid','date','payee','amount','approved',
            'memo','comment','account','category')

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        user = self.context['request'].user
        category_name = self.context['request'].data.get('category_name')
        if category_name:
            category = utils.get_object_or_none(Category, user=user, name__iexact=category_name)
            if not category:
                raise serializers.ValidationError("Unknown category '%s'." % category_name)
            instance.category = category
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


class KeyValueSerializer(DynamicFieldsSerializer):
    class Meta:
        model = KeyValue
        fields = ('key','value','url')


class KeyValueViewSet(viewsets.ModelViewSet):
    queryset = KeyValue.objects.order_by('key')
    serializer_class = KeyValueSerializer
    permission_classes = [IsAuthenticated]
    list_fields = KeyValueSerializer.Meta.fields


@api_view(['get'])
def budget(request):
    root = reverse('api-root', request=request)
    return Response({
        'budget/accounts': f'{root}budget/accounts',
        'budget/categories': f'{root}budget/categories',
        'budget/keyvalue': f'{root}budget/keyvalue',
        'budget/transactions': f'{root}budget/transactions',
        'budget/upload': f'{root}budget/upload',
    })


@api_view(['put'])
@permission_classes([IsAuthenticated])
def upload(request, format=None):
    """ Upload new transactions to the budget app. """
    trxmanager = TransactionManager()
    for fileobj in request.FILES.values():
        trxmanager.import_qfx(fileobj.name, fileobj.file)
    return Response(trxmanager.get_status())
