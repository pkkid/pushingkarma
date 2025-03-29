# encoding: utf-8
import logging
from decimal import Decimal
from django_searchquery import searchfields as sf
from django_searchquery.search import Search
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from ninja import Router
from ninja.errors import HttpError
from pk.utils.django import reverse
from pk.utils.ninja import PageSchema, paginate
from .models import Account, Category, Transaction
from .schemas import AccountSchema, CategorySchema, TransactionSchema
from .schemas import SortSchema
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
    item = get_object_or_404(Account, user=request.user, id=accountid).order_by('sortid')
    itemdict = model_to_dict(item)
    itemdict['url'] = reverse(request, 'api:account', accountid=item.id)
    return itemdict


@router.get('/accounts', response=PageSchema(AccountSchema), exclude_unset=True)
def list_accounts(request, search:str='', page:int=1):
    """ List accounts for the logged in user.
        • search: Filter accounts by search string.
        • page: Page number of results to return
    """
    items = Account.objects.filter(user=request.user).order_by('sortid')
    if search: items = Search(ACCOUNTSEARCHFIELDS).get_queryset(items, search)
    data = paginate(request, items, page=page, perpage=100)
    for i in range(len(data['items'])):
        item = data['items'][i]
        itemdict = model_to_dict(item)
        itemdict['url'] = reverse(request, 'api:account', accountid=item.id)
        data['items'][i] = itemdict
    return data


@router.patch('/sort_accounts', response=PageSchema(AccountSchema), exclude_unset=True)
def sort_accounts(request, data:SortSchema):
    """ Sort accounts for the logged in user.
        • sort: List of account ids in the desired order
    """
    items = Account.objects.filter(user=request.user, id__in=data.sortlist)
    if len(items) != len(data.sortlist):
        raise HttpError(409, 'Account ids do not match user accounts')
    # updates = []
    # itemsdict = {item.id:item for item in items}
    # for i in range(len(data.sortlist)):
    #     item = itemsdict[data.sortlist[i]]
    #     if item.sortid != i+1:
    #         item.sortid = i+1
    #         updates.append(item)
    if updates := _sort_items(items, data.sortlist):
        log.info(f'Sorting {len(updates)} accounts for account {request.user.email}')
        Account.objects.bulk_update(updates, ['sortid'])
    return list_accounts(request)


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
    items = Category.objects.filter(user=request.user).order_by('sortid')
    if search: items = Search(CATEGORYSEARCHFIELDS).get_queryset(items, search)
    data = paginate(request, items, page=page, perpage=100)
    for i in range(len(data['items'])):
        item = data['items'][i]
        itemdict = model_to_dict(item)
        itemdict['url'] = reverse(request, 'api:category', categoryid=item.id)
        data['items'][i] = itemdict
    return data


@router.patch('/sort_categories', response=PageSchema(CategorySchema), exclude_unset=True)
def sort_categories(request, data:SortSchema):
    """ Sort categories for the logged in user.
        • sort: List of category ids in the desired order
    """
    items = Category.objects.filter(user=request.user, id__in=data.sortlist)
    if len(items) != len(data.sortlist):
        raise HttpError(409, 'Category ids do not match user categories')
    if updates := _sort_items(items, data.sortlist):
        log.info(f'Sorting {len(updates)} categories for account {request.user.email}')
        Category.objects.bulk_update(updates, ['sortid'])
    return list_categories(request)


@router.get('/transactions/{transactionid}', response=TransactionSchema, exclude_unset=True, url_name='transaction')
def get_transaction(request, transactionid:int):
    """ List details for the specified transaction.
        • transactionid: Transaction id
    """
    item = get_object_or_404(Transaction, user=request.user, id=transactionid)
    itemdict = model_to_dict(item)
    itemdict['url'] = reverse(request, 'api:transaction', transactionid=item.id)
    itemdict['account'] = dict(
        url = reverse(request, 'api:account', accountid=item.account.id),
        id = item.account.id,
        name = item.account.name,
    )
    itemdict['category'] = dict(
        url = reverse(request, 'api:category', categoryid=item.category.id),
        id = item.category.id,
        name = item.category.name,
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
            url = reverse(request, 'api:account', accountid=item.account.id),
            name = item.account.name,
        )
        itemdict['category'] = dict(
            url = reverse(request, 'api:category', categoryid=item.category.id),
            name = item.category.name,
        ) if item.category else None
        data['items'][i] = itemdict
    return data


def _sort_items(items, sortlist, itemid='id', sortkey='sortid'):
    """ Sort items in the order specified by sortlist.
        • itemsdict: Dictionary of items to sort
        • sortlist: List of item ids in the desired order
        • itemid: Item id field to use for sorting
        • sortkey: Item sort field to update
    """
    updates = []
    itemsdict = {getattr(item, itemid):item for item in items}
    for i in range(len(sortlist)):
        item = itemsdict[sortlist[i]]
        sortid = getattr(item, sortkey)
        if sortid != i+1:
            setattr(item, sortkey, i+1)
            updates.append(item)
    return updates
