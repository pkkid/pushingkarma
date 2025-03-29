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
from .schemas import AccountSchema, CategorySchema, TransactionSchema
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
    sf.StrField('account', 'account__name', desc='Account name', generic=True),
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


@router.get('/transactions/{transactionid}', response=TransactionSchema, exclude_unset=True, url_name='transaction')
def get_transaction(request, transactionid:int):
    """ List details for the specified transaction.
        • transactionid: Transaction id
    """
    item = get_object_or_404(Transaction, user=request.user, id=transactionid)
    itemdict = model_to_dict(item)
    itemdict['url'] = reverse(request, 'api:transaction', transactionid=item.id)
    itemdict['account'] = dict(
        name = item.account.name,
        url = reverse(request, 'api:account', accountid=item.account.id))
    itemdict['category'] = dict(
        name = item.category.name,
        url = reverse(request, 'api:category', categoryid=item.category.id)
    ) if item.category else None
    return itemdict


@router.get('/transactions', response=PageSchema(TransactionSchema), exclude_unset=True)
def list_transactions(request, search:str='', page:int=1):
    """ List transactions for the logged in user.
        • search: Filter transactions by search string.
        • page: Page number of results to return
    """
    items = Transaction.objects.filter(user=request.user).order_by('-date', 'payee')
    if search: items = Search(TRANSACTIONSEARCHFIELDS).get_queryset(items, search)
    data = paginate(request, items, page=page, perpage=100)
    for i in range(len(data['items'])):
        item = data['items'][i]
        itemdict = model_to_dict(item)
        itemdict['url'] = reverse(request, 'api:transaction', transactionid=item.id)
        itemdict['account'] = dict(
            name = item.account.name,
            url = reverse(request, 'api:account', accountid=item.account.id))
        itemdict['category'] = dict(
            name = item.category.name,
            url = reverse(request, 'api:category', categoryid=item.category.id)
        ) if item.category else None
        data['items'][i] = itemdict
    return data
