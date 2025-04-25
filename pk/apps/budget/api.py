# encoding: utf-8
import logging
from django_searchquery import searchfields as sf
from django_searchquery.search import Search
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from ninja import Body, File, Path, Query, Router
from ninja.files import UploadedFile
from ninja.errors import HttpError
from pk.utils.ninja import PageSchema, paginate
from typing import List
from .trxmanager import TransactionManager
from .models import Account, Category, Transaction
from .schemas import AccountSchema, AccountPatchSchema
from .schemas import CategorySchema, CategoryPatchSchema
from .schemas import TransactionSchema, SortSchema, ImportResponseSchema
log = logging.getLogger(__name__)
router = Router()

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


# ---------------
# Accounts
# ---------------

@router.get('/accounts/{pk}', response=AccountSchema, exclude_unset=True, url_name='account')
def get_account(request,
      pk: int=Path(..., description='Primary key of account to get')):
    """ List details for the specified account. """
    account = get_object_or_404(Account, user=request.user, id=pk)
    response = AccountSchema.from_orm(account)
    return response


@router.patch('/accounts/{pk}', response=AccountSchema, exclude_unset=True)
def update_account(request,
      pk: int=Path(..., description='Primary key of account to update'),
      data: AccountPatchSchema=Body(...)):
    """ Update the specified account. """
    item = get_object_or_404(Account, user=request.user, id=pk)
    if data.name: item.name = data.name
    if data.rules: item.rules = data.rules.dict(exclude_none=True)
    item.save()
    return get_account(request, pk)


@router.delete('/accounts/{pk}', response=None)
def delete_account(request,
      pk: int=Path(..., description='Primary key of account to delete')):
    """ Delete the specified account. """
    get_object_or_404(Account, user=request.user, id=pk).delete()
    return HttpResponse(status=204)


@router.get('/accounts', response=PageSchema(AccountSchema), exclude_unset=True)
def list_accounts(request,
      search: str=Query('', description='Search term to filter accounts'),
      page: int=Query(1, description='Page number of results to return')):
    """ List accounts for the logged in user. """
    accounts = Account.objects.filter(user=request.user).order_by('sortid')
    accounts = accounts.select_related('summary')
    if search:
        accounts = Search(ACCOUNTSEARCHFIELDS).get_queryset(accounts, search)
    data = paginate(request, accounts, page=page, perpage=100)
    return data


@router.patch('/sort_accounts', response=PageSchema(AccountSchema), exclude_unset=True)
def sort_accounts(request, data:SortSchema=Body(...)):
    """ Sort accounts for the logged in user. """
    items = Account.objects.filter(user=request.user, id__in=data.sortlist)
    if len(items) != len(data.sortlist):
        raise HttpError(409, 'Account ids do not match user accounts')
    if updates := _sort_items(items, data.sortlist):
        log.info(f'Sorting {len(updates)} accounts for account {request.user.email}')
        Account.objects.bulk_update(updates, ['sortid'])
    return list_accounts(request, '', 1)


# ---------------
# Categories
# ---------------

@router.get('/categories/{pk}', response=CategorySchema, exclude_unset=True, url_name='category')
def get_category(request,
      pk: int=Path(..., description='Primary key of category to get')):
    """ List details for the specified category. """
    category = get_object_or_404(Category, user=request.user, id=pk)
    response = CategorySchema.from_orm(category)
    return response


@router.patch('/categories/{pk}', response=CategorySchema, exclude_unset=True)
def update_category(request,
      pk: int=Path(..., description='Primary key of category to update'),
      data: CategoryPatchSchema=Body(...)):  # noqa
    """ Update the specified category. """
    item = get_object_or_404(Category, user=request.user, id=pk)
    if data.name: item.name = data.name
    item.save()
    return get_category(request, pk)


@router.delete('/categories/{pk}', response=None)
def delete_category(request,
      pk: int=Path(..., description='Primary key of category to delete')):
    """ Update the specified category. """
    get_object_or_404(Category, user=request.user, id=pk).delete()
    return HttpResponse(status=204)


@router.get('/categories', response=PageSchema(CategorySchema), exclude_unset=True)
def list_categories(request,
      search: str=Query('', description='Search term to filter categories'),
      page: int=Query(1, description='Page number of results to return')):
    """ List categories for the logged in user. """
    categories = Category.objects.filter(user=request.user).order_by('sortid')
    if search:
        categories = Search(CATEGORYSEARCHFIELDS).get_queryset(categories, search)
    data = paginate(request, categories, page=page, perpage=100)
    return data


@router.patch('/sort_categories', response=PageSchema(CategorySchema), exclude_unset=True)
def sort_categories(request, data:SortSchema=Body(...)):
    """ Sort categories for the logged in user. """
    items = Category.objects.filter(user=request.user, id__in=data.sortlist)
    if len(items) != len(data.sortlist):
        raise HttpError(409, 'Category ids do not match user categories')
    if updates := _sort_items(items, data.sortlist):
        log.info(f'Sorting {len(updates)} categories for account {request.user.email}')
        Category.objects.bulk_update(updates, ['sortid'])
    return list_categories(request, '', 1)


# ---------------
# Transactions
# ---------------

@router.get('/transactions/{pk}', response=TransactionSchema, exclude_unset=True, url_name='transaction')
def get_transaction(request,
      pk: int=Path(..., description='Primary key of transaction to get')):
    """ List details for the specified transaction. """
    trx = get_object_or_404(Transaction, user=request.user, id=pk)
    response = TransactionSchema.from_orm(trx)
    response.account = dict(url=trx.account.url, id=trx.account.id, name=trx.account.name)
    response.category = dict(url=trx.category.url, id=trx.category.id, name=trx.category.name) if trx.category else None
    return response


@router.get('/transactions', response=PageSchema(TransactionSchema), exclude_unset=True)
def list_transactions(request,
      search: str=Query('', description='Search term to filter transactions'),
      page: int=Query(1, description='Page number of results to return')):
    """ List transactions for the logged in user. """
    trxs = Transaction.objects.filter(user=request.user)
    trxs = trxs.select_related('account', 'category')
    trxs = trxs.order_by('-date', 'payee')
    if search:
        trxs = Search(TRANSACTIONSEARCHFIELDS).get_queryset(trxs, search)
    response = paginate(request, trxs, page=page, perpage=100)
    for i in range(len(response['items'])):
        trx = response['items'][i]
        item = model_to_dict(response['items'][i])
        item['url'] = trx.url
        item['account'] = dict(id=trx.account.id, url=trx.account.url, name=trx.account.name)
        item['category'] = dict(id=trx.category.id, url=trx.category.url, name=trx.category.name) if trx.category else None
        response['items'][i] = item
    return response


@router.post('/import_transactions', response=List[ImportResponseSchema], exclude_unset=True)
def import_transactions(request,
      files: List[UploadedFile]=File(..., description='List of transaction files to import (.csv or .qfx)'),
      safe: bool=Body(False, description='Safe import, unique transactions based on date, payee and amount.')):
    """ Upload new transactions to the budget app. This is a file upload (multipart/form-data) endpoint. """
    response = []
    for fileobj in files:
        trxmanager = TransactionManager(request.user, safe, save=True)
        metrics = trxmanager.import_file(fileobj.name, fileobj.file)
        response.append(metrics)
    return response


def _sort_items(items, sortlist, itemid='id', sortkey='sortid'):
    """ Sort items in the order specified by sortlist.
        itemsdict: Dictionary of items to sort
        sortlist: List of item ids in the desired order
        itemid: Item id field to use for sorting
        sortkey: Item sort field to update
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
