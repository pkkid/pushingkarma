# encoding: utf-8
from decimal import Decimal
from django_searchquery import searchfields as sf
from pk import utils
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Account


IGNORED = 'Ignored'
RESET_DECIMAL = Decimal('-99999.99')
RESET = ['_RESET', RESET_DECIMAL]
REVERSE = True   # Set 'True' or 'False' for reversed month order.
ACCOUNTSEARCHFIELDS = [
    sf.StrField('name', 'name', desc='Account name', generic=True),
    sf.StrField('fid', 'fid', desc='Financial institution id', generic=True),
    sf.StrField('type', 'type', desc='Account type (bank, credit)'),
    sf.NumField('balance', 'balance', desc='Account balance'),
    sf.DateField('updated', 'balancedt', desc='Last update'),
]
# TRANSACTIONSEARCHFIELDS = {
#     'bank': SearchField(FIELDTYPES.STR, 'account__name'),
#     'date': SearchField(FIELDTYPES.DATE, 'date'),
#     'payee': SearchField(FIELDTYPES.STR, 'payee'),
#     'category': SearchField(FIELDTYPES.STR, 'category__name'),
#     'amount': SearchField(FIELDTYPES.NUM, 'amount'),
#     'approved': SearchField(FIELDTYPES.BOOL, 'approved'),
#     'comment': SearchField(FIELDTYPES.STR, 'comment'),
# }


class AccountSerializer(utils.DynamicFieldsSerializer):
    class Meta:
        model = Account
        fields = ('id','url','name','fid','type','payee','balance','balancedt')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        account = Account(**validated_data)
        account.save()
        return account


class AccountsViewSet(viewsets.ModelViewSet, utils.ViewSetMixin):
    serializer_class = AccountSerializer
    queryset = Account.objects.order_by('name')
    permission_classes = [IsAuthenticated]
    list_fields = AccountSerializer.Meta.fields
    # pagination_class = utils.CustomPageNumberPagination

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user).order_by('name')

    def list(self, request, *args, **kwargs):
        return self.list_response(request, paginated=True, searchfields=ACCOUNTSEARCHFIELDS)


# class CategorySerializer(DynamicFieldsSerializer):
#     class Meta:
#         model = Category
#         fields = ('id','url','name','sortindex','budget','comment','exclude_budget')
    
#     def to_internal_value(self, data):
#         if data.get('budget'):
#             data['budget'] = clean_amount(data['budget'])
#         return super(CategorySerializer, self).to_internal_value(data)
    
#     def create(self, validated_data):
#         validated_data['user'] = self.context['request'].user
#         account = Category(**validated_data)
#         account.save()
#         return account


# class CategoriesViewSet(viewsets.ModelViewSet, utils.ViewSetMixin):
#     queryset = Category.objects.order_by('-sortindex')
#     serializer_class = CategorySerializer
#     permission_classes = [IsAuthenticated]
#     list_fields = CategorySerializer.Meta.fields

#     def annotations(self):
#         year_maxdate = datetime.date.today().replace(day=1)
#         year_mindate = year_maxdate - relativedelta(years=1)
#         return {
#             'num_transactions': Count('transaction'),
#             'year_transactions': Count('transaction', filter=Q(transaction__date__gte=year_mindate, transaction__date__lt=year_maxdate)),
#             'year_total': Sum('transaction__amount', filter=Q(transaction__date__gte=year_mindate, transaction__date__lt=year_maxdate)),
#             'year_average': Cast(F('year_total') / 12, DecimalField(max_digits=9, decimal_places=2))
#         }
    
#     def get_queryset(self):
#         return Category.objects.filter(user=self.request.user).order_by('-sortindex')

#     def list(self, request, *args, **kwargs):
#         categories = self.get_queryset().order_by('sortindex')
#         page = self.paginate_queryset(categories)
#         serializer = CategorySerializer(page, context={'request':request}, many=True, fields=self.list_fields)
#         response = self.get_paginated_response(serializer.data)
#         utils.move_to_end(response.data, 'results')
#         return self.append_metadata(response, categories)


# class TransactionSerializer(utils.DynamicFieldsSerializer):
#     account = PartialFieldsSerializer(AccountSerializer, ('url','name'))
#     category = PartialFieldsSerializer(CategorySerializer, ('url','name','budget'))

#     class Meta:
#         model = Transaction
#         fields = ('id','url','trxid','date','payee','amount','approved',
#             'comment','account','category')
    
#     def to_internal_value(self, data):
#         if data.get('amount') in RESET:
#             data['amount'] = RESET_DECIMAL
#         elif data.get('amount'):
#             data['amount'] = clean_amount(data['amount'])
#         return super(TransactionSerializer, self).to_internal_value(data)

#     def update(self, instance, validated_data):
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         user = self.context['request'].user
#         # Update category_name
#         category_name = self.context['request'].data.get('category_name')
#         if category_name is not None:
#             instance.category = None
#             if category_name != '':
#                 instance.category = utils.get_object_or_none(Category, user=user, name__iexact=category_name)
#                 if not instance.category:
#                     raise serializers.ValidationError("Unknown category '%s'." % category_name)
#         # Some values can be reset
#         if self.context['request'].data.get('date') in RESET: instance.date = instance.original_date
#         if self.context['request'].data.get('payee') in RESET: instance.payee = instance.original_payee
#         if self.context['request'].data.get('amount') in RESET: instance.amount = instance.original_amount
#         instance.save()
#         return instance


# class TransactionsViewSet(viewsets.ModelViewSet, utils.ViewSetMixin):
#     queryset = Transaction.objects.order_by('-date')
#     serializer_class = TransactionSerializer
#     permission_classes = [IsAuthenticated]
#     list_fields = TransactionSerializer.Meta.fields

#     def list(self, request, *args, **kwargs):
#         searchdata = {}
#         searchstr = request.GET.get('search')
#         transactions = Transaction.objects.filter(user=request.user).order_by('-date', 'payee', 'id')
#         if searchstr:
#             search = Search(transactions, TRANSACTIONSEARCHFIELDS, searchstr)
#             transactions = search.queryset()
#             searchdata = {'searchstr':searchstr, 'errors':', '.join(search.errors),
#                 'datefilters':' AND '.join(search.datefilters)}
#         page = self.paginate_queryset(transactions)
#         serializer = TransactionSerializer(page, context={'request':request}, many=True, fields=self.list_fields)
#         response = self.get_paginated_response(serializer.data)
#         response.data.update(searchdata)
#         response.data['unapproved'] = transactions.filter(approved=False).count()
#         response.data['uncategorized'] = transactions.filter(category_id=None).count()
#         utils.move_to_end(response.data, 'previous','next','upload','results')
#         return response
    
#     def summary():
#         pass


# def clean_amount(value):
#     """ Clean a USD string such as -$99.99 to a Decimal value. """
#     if isinstance(value, str):
#         value = value.replace('$', '')
#         value = value.replace(',', '')
#         return Decimal(value)
#     if isinstance(value, (int, float)):
#         return Decimal(value)
#     return value
