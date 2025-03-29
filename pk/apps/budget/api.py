# encoding: utf-8
import logging
from decimal import Decimal
from django_searchquery import searchfields as sf
from django_searchquery.search import Search
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from ninja import Router
from pk.utils.django import reverse
from pk.utils.ninja import PageSchema, paginate
from .models import Account, Category, Transaction
from .schemas import AccountSchema, CategorySchema
log = logging.getLogger(__name__)
router = Router()


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
CATEGORYSEARCHFIELDS = [
    sf.StrField('name', 'name', desc='Category name', generic=True),
    sf.StrField('comment', 'comment', desc='Comment'),
]
TRANSACTIONSEARCHFIELDS = {
    sf.StrField('bank', 'account__name', desc='Bank name', generic=True),
    sf.DateField('date', 'date', desc='Transaction date'),
    sf.StrField('payee', 'payee', desc='Transacation payee', generic=True),
    sf.StrField('category', 'category__name', desc='Transaction category', generic=True),
    sf.NumField('amount', 'amount', desc='Transaction amount'),
    sf.BoolField('approved', 'approved', desc='User approved'),
    sf.StrField('comment', 'comment', desc='Comment', generic=True),
}


@router.get('/accounts/{accountid}', response=AccountSchema, exclude_unset=True, url_name='account')
def get_account(request, accountid:int):
    """ List details for the specified account.
        • accountid: Account id
    """
    item = get_object_or_404(Account, user=request.user, id=accountid)
    itemdict = model_to_dict(item)
    itemdict['url'] = reverse(request, 'api:account', accountid=item.id)
    return itemdict


@router.get('/accounts', response=PageSchema(AccountSchema), exclude_unset=True)
def list_accounts(request, search:str='', page:int=1):
    """ List accounts for the logged in user.
        • search: Filter accounts by search string.
        • page: Page number of results to return
    """
    items = Account.objects.filter(user=request.user).order_by('name')
    if search: items = Search(ACCOUNTSEARCHFIELDS).get_queryset(items, search)
    data = paginate(request, items, page=page, perpage=100)
    for i in range(len(data['items'])):
        item = data['items'][i]
        itemdict = model_to_dict(item)
        itemdict['url'] = reverse(request, 'api:account', accountid=item.id)
        data['items'][i] = itemdict
    return data


@router.get('/categories/{categoryid}', response=CategorySchema, exclude_unset=True, url_name='category')
def get_category(request, categoryid:int):
    """ List details for the specified category.
        • categoryid: Category id
    """
    item = get_object_or_404(Category, user=request.user, id=categoryid)
    itemdict = model_to_dict(item)
    itemdict['url'] = reverse(request, 'api:category', categoryid=item.id)
    return itemdict


@router.get('/categories', response=PageSchema(CategorySchema), exclude_unset=True)
def list_categories(request, search:str='', page:int=1):
    """ List categories for the logged in user.
        • search: Filter categories by search string.
        • page: Page number of results to return
    """
    items = Category.objects.filter(user=request.user).order_by('sortindex')
    if search: items = Search(CATEGORYSEARCHFIELDS).get_queryset(items, search)
    data = paginate(request, items, page=page, perpage=100)
    for i in range(len(data['items'])):
        item = data['items'][i]
        itemdict = model_to_dict(item)
        itemdict['url'] = reverse(request, 'api:category', categoryid=item.id)
        data['items'][i] = itemdict
    return data



# -------------------------------
# from decimal import Decimal
# from django_searchquery import searchfields as sf
# from pk.utils import utils
# from rest_framework import viewsets
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.exceptions import ValidationError
# from .models import Account, Category, Transaction

# class AccountSerializer(utils.DynamicFieldsSerializer):
#     class Meta:
#         model = Account
#         fields = ('id', 'url', 'name', 'fid', 'type', 'payee', 'balance', 'balancedt')

#     def create(self, validated_data):
#         validated_data['user'] = self.context['request'].user
#         account = Account(**validated_data)
#         account.save()
#         return account


# class AccountsViewSet(viewsets.ModelViewSet, utils.ViewSetMixin):
#     """ Rest endpoint to list or modifiy user's financial accounts. """
#     serializer_class = AccountSerializer
#     permission_classes = [IsAuthenticated]
#     list_fields = AccountSerializer.Meta.fields

#     def get_queryset(self):
#         return Account.objects.filter(user=self.request.user).order_by('name')

#     def list(self, request, *args, **kwargs):
#         return self.list_response(request, paginated=True, searchfields=ACCOUNTSEARCHFIELDS)


# class CategorySerializer(utils.DynamicFieldsSerializer):
#     class Meta:
#         model = Category
#         fields = ('id', 'url', 'name', 'sortindex', 'budget', 'comment', 'exclude_budget')
    
#     def create(self, validated_data):
#         validated_data['user'] = self.context['request'].user
#         account = Category(**validated_data)
#         account.save()
#         return account


# class CategoriesViewSet(viewsets.ModelViewSet, utils.ViewSetMixin):
#     """ Rest endpoint to list or modifiy user's budget categories. """
#     serializer_class = CategorySerializer
#     permission_classes = [IsAuthenticated]
#     list_fields = CategorySerializer.Meta.fields
    
#     def get_queryset(self):
#         return Category.objects.filter(user=self.request.user).order_by('sortindex')

#     def to_internal_value(self, data):
#         if data.get('budget'): data['budget'] = utils.clean_amount(data['budget'])
#         return super(CategorySerializer, self).to_internal_value(data)

#     def list(self, request, *args, **kwargs):
#         return self.list_response(request, paginated=True, searchfields=CATEGORYSEARCHFIELDS)


# class TransactionSerializer(utils.DynamicFieldsSerializer):
#     category = utils.PartialFieldsSerializer(CategorySerializer, ('url', 'name', 'budget'))
#     account = utils.PartialFieldsSerializer(AccountSerializer, ('url', 'name'))

#     class Meta:
#         model = Transaction
#         fields = ('id', 'url', 'trxid', 'date', 'payee', 'amount', 'approved',
#             'comment', 'category', 'account')

#     def to_internal_value(self, data):
#         if data.get('amount') in RESET: data['amount'] = RESET_DECIMAL
#         elif data.get('amount'): data['amount'] = utils.clean_amount(data['amount'])
#         return super(TransactionSerializer, self).to_internal_value(data)

#     def update(self, instance, validated_data):
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         user = self.context['request'].user
#         # Update category_name
#         category_name = self.context['request'].data.get('category_name')
#         # TODO: I think the below can just be the following:
#         # instance.category = utils.get_object_or_none(Category, user=user, name__iexact=category_name)
#         # if not instance.category:
#         #     raise ValidationError("Unknown category '%s'." % category_name)
#         if category_name is not None:
#             instance.category = None
#             if category_name != '':
#                 instance.category = utils.get_object_or_none(Category, user=user, name__iexact=category_name)
#                 if not instance.category:
#                     raise ValidationError("Unknown category '%s'." % category_name)
#         # Some values can be reset
#         if self.context['request'].data.get('date') in RESET: instance.date = instance.original_date
#         if self.context['request'].data.get('payee') in RESET: instance.payee = instance.original_payee
#         if self.context['request'].data.get('amount') in RESET: instance.amount = instance.original_amount
#         instance.save()
#         return instance


# class TransactionsViewSet(viewsets.ModelViewSet, utils.ViewSetMixin):
#     """ Rest endpoint to list or modifiy user's transactions. """
#     serializer_class = TransactionSerializer
#     permission_classes = [IsAuthenticated]
#     list_fields = TransactionSerializer.Meta.fields

#     def get_queryset(self):
#         transactions = Transaction.objects.filter(user=self.request.user)
#         transactions = transactions.select_related('category')
#         transactions = transactions.select_related('account')
#         return transactions.order_by('-date')

#     def list(self, request, *args, **kwargs):
#         return self.list_response(request, paginated=True, searchfields=TRANSACTIONSEARCHFIELDS)
