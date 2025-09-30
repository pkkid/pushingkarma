# encoding: utf-8
import logging
from datetime import datetime
from django_searchquery import searchfields as sf
from django_searchquery.search import Search
from django.db.models import Count, Case, When, Max, Min, Sum, DecimalField, IntegerField
from django.db.models.functions import TruncMonth
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from itertools import groupby
from ninja import Body, File, Path, Query, Router
from ninja.errors import HttpError
from ninja.files import UploadedFile
from pk.utils.utils import add_months, first_of_month
from pk.utils.django import get_object_or_none
from pk.utils.ninja import PageSchema, paginate
from typing import List
from . import schemas, utils
from .models import Account, Category, Transaction
from .trxmanager import TransactionManager
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

@router.get('/accounts/{pk}', response=schemas.AccountSchema, exclude_unset=True, url_name='account')
def get_account(request,
      pk: int=Path(..., description='Primary key of account to get')):
    """ List details for the specified account. """
    account = get_object_or_404(Account, user=request.user, id=pk)
    response = schemas.AccountSchema.from_orm(account)
    return response


@router.patch('/accounts/{pk}', response=schemas.AccountSchema, exclude_unset=True)
def update_account(request,
      pk: int=Path(..., description='Primary key of account to update'),
      data: schemas.AccountPatchSchema=Body(...)):
    """ Update the specified account. """
    item = get_object_or_404(Account, user=request.user, id=pk)
    fields = data.dict(exclude_unset=True)
    if 'name' in fields: item.name = fields['name']
    if 'rules' in fields: item.rules = fields['rules']
    item.save()
    return get_account(request, pk)


@router.delete('/accounts/{pk}', response=None)
def delete_account(request,
      pk: int=Path(..., description='Primary key of account to delete')):
    """ Delete the specified account. """
    get_object_or_404(Account, user=request.user, id=pk).delete()
    return HttpResponse(status=204)


@router.get('/accounts', response=PageSchema(schemas.AccountSchema), exclude_unset=True)
def list_accounts(request,
      search: str=Query('', description='Search term to filter accounts'),
      page: int=Query(1, description='Page number of results to return')):
    """ List accounts for the logged in user. """
    accounts = Account.objects.filter(user=request.user).order_by('sortid')
    if search:
        accounts = Search(ACCOUNTSEARCHFIELDS).get_queryset(accounts, search)
    response = paginate(request, accounts, page=page, perpage=100)
    for i in range(len(response['items'])):
        account = response['items'][i]
        item = model_to_dict(account)
        item['url'] = account.url
        item['summary'] = account.get_year_summary()
        response['items'][i] = item
    return response


@router.post('/accounts', response=schemas.AccountSchema, exclude_unset=True)
def create_account(request, data: schemas.AccountPatchSchema=Body(...)):
    """ Create a new account for the logged in user. """
    item = Account(user=request.user, **data.dict(exclude_unset=True))
    item.save()
    return get_account(request, item.id)


@router.patch('/sort_accounts', response=PageSchema(schemas.AccountSchema), exclude_unset=True)
def sort_accounts(request, data:schemas.SortSchema=Body(...)):
    """ Sort accounts for the logged in user. """
    items = Account.objects.filter(user=request.user, id__in=data.sortlist)
    if len(items) != len(data.sortlist):
        raise HttpError(409, 'Account ids do not match user accounts')
    if updates := utils.sort_items(items, data.sortlist):
        log.info(f'Sorting {len(updates)} accounts for account {request.user.email}')
        Account.objects.bulk_update(updates, ['sortid'])
    return list_accounts(request, '', 1)


# ---------------
# Categories
# ---------------

@router.get('/categories/{pk}', response=schemas.CategorySchema, exclude_unset=True, url_name='category')
def get_category(request,
      pk: int=Path(..., description='Primary key of category to get')):
    """ List details for the specified category. """
    category = get_object_or_404(Category, user=request.user, id=pk)
    response = schemas.CategorySchema.from_orm(category)
    return response


@router.patch('/categories/{pk}', response=schemas.CategorySchema, exclude_unset=True)
def update_category(request,
      pk: int=Path(..., description='Primary key of category to update'),
      data: schemas.CategoryPatchSchema=Body(...)):  # noqa
    """ Update the specified category. """
    item = get_object_or_404(Category, user=request.user, id=pk)
    fields = data.dict(exclude_unset=True)
    if 'name' in fields: item.name = fields['name']
    item.save()
    return get_category(request, pk)


@router.delete('/categories/{pk}', response=None)
def delete_category(request,
      pk: int=Path(..., description='Primary key of category to delete')):
    """ Update the specified category. """
    get_object_or_404(Category, user=request.user, id=pk).delete()
    return HttpResponse(status=204)


@router.get('/categories', response=PageSchema(schemas.CategorySchema), exclude_unset=True)
def list_categories(request,
      search: str=Query('', description='Search term to filter categories'),
      page: int=Query(1, description='Page number of results to return')):
    """ List categories for the logged in user. """
    categories = Category.objects.filter(user=request.user).order_by('sortid')
    if search:
        categories = Search(CATEGORYSEARCHFIELDS).get_queryset(categories, search)
    data = paginate(request, categories, page=page, perpage=100)
    return data


@router.post('/categories', response=schemas.CategorySchema, exclude_unset=True)
def create_category(request, data: schemas.CategoryPatchSchema=Body(...)):
    """ Create a new category for the logged in user. """
    item = Category(user=request.user, **data.dict(exclude_unset=True))
    item.save()
    return get_category(request, item.id)


@router.patch('/sort_categories', response=PageSchema(schemas.CategorySchema), exclude_unset=True)
def sort_categories(request, data:schemas.SortSchema=Body(...)):
    """ Sort categories for the logged in user. """
    items = Category.objects.filter(user=request.user, id__in=data.sortlist)
    if len(items) != len(data.sortlist):
        raise HttpError(409, 'Category ids do not match user categories')
    if updates := utils.sort_items(items, data.sortlist):
        log.info(f'Sorting {len(updates)} categories for account {request.user.email}')
        Category.objects.bulk_update(updates, ['sortid'])
    return list_categories(request, '', 1)


# ---------------
# Transactions
# ---------------

@router.get('/transactions/{pk}', response=schemas.TransactionSchema, exclude_unset=True, url_name='transaction')
def get_transaction(request,
      pk: int=Path(..., description='Primary key of transaction to get')):
    """ List details for the specified transaction. """
    trx = get_object_or_404(Transaction, user=request.user, id=pk)
    response = schemas.TransactionSchema.from_orm(trx)
    response.account = dict(url=trx.account.url, id=trx.account.id, name=trx.account.name)
    response.category = dict(url=trx.category.url, id=trx.category.id, name=trx.category.name) if trx.category else None
    return response


@router.patch('/transactions/{pk}', response=schemas.TransactionSchema, exclude_unset=True)
def update_transaction(request,
      pk: int=Path(..., description='Primary key of transaction to update'),
      data: schemas.TransactionPatchSchema=Body(...)):  # noqa
    """ Update the specified transaction. """
    item = get_object_or_404(Transaction, user=request.user, id=pk)
    fields = data.dict(exclude_unset=True)
    print(fields)
    if 'date' in fields: item.date = fields['date']
    if 'payee' in fields: item.payee = fields['payee']
    if 'amount' in fields: item.amount = fields['amount']
    if 'approved' in fields: item.approved = fields['approved']
    if 'comment' in fields: item.comment = fields['comment']
    if 'category' in fields:
        category = get_object_or_none(Category, user=request.user, name__iexact=fields['category'])
        if not category and fields['category'] != '':
            raise HttpError(409, f'Category "{fields['category']}" not found')
        item.category = category
    item.save()
    return get_transaction(request, pk)


@router.get('/transactions', response=PageSchema(schemas.TransactionSchema), exclude_unset=True)
def list_transactions(request,
      search: str=Query('', description='Search term to filter transactions'),
      page: int=Query(1, description='Page number of results to return')):
    """ List transactions for the logged in user. """
    trxs = Transaction.objects.filter(user=request.user)
    trxs = trxs.select_related('account', 'category')
    trxs = trxs.order_by('-date', 'payee')
    if search:
        searchobj = Search(TRANSACTIONSEARCHFIELDS)
        trxs = searchobj.get_queryset(trxs, search)
    response = paginate(request, trxs, page=page, perpage=100)
    for i in range(len(response['items'])):
        trx = response['items'][i]
        item = model_to_dict(trx)
        item['url'] = trx.url
        item['account'] = dict(id=trx.account.id, url=trx.account.url, name=trx.account.name)
        item['category'] = dict(id=trx.category.id, url=trx.category.url, name=trx.category.name) if trx.category else None
        if trx.category and trx.category.exclude: item['category']['exclude'] = True
        response['items'][i] = item
    return response


@router.get('/summarize_transactions', response=schemas.TransactionSummarySchema)
def summarize_transactions(request,
      search: str=Query('', description='Search term to filter transactions')):
    """ Summarizes transactions for the logged in user. """
    # Get base queryset and apply search filter
    trxs = Transaction.objects.filter(user=request.user)
    searchobj = None
    if search:
        searchobj = Search(TRANSACTIONSEARCHFIELDS)
        trxs = searchobj.get_queryset(trxs, search)
        log.info(searchobj.meta)
    # Calculate aggregated totals
    totals = trxs.aggregate(
        total_spent=Sum(Case(When(amount__lt=0, then='amount'), default=0, output_field=DecimalField())),
        total_income=Sum(Case(When(amount__gt=0, then='amount'), default=0, output_field=DecimalField())),
        total_amount=Sum('amount'),
        uncategorized_count=Count(Case(When(category__isnull=True, then=1), output_field=IntegerField())),
        uncategorized_amount=Sum(Case(When(category__isnull=True, then='amount'), default=0, output_field=DecimalField())),
        unapproved_count=Count(Case(When(approved=False, then=1), output_field=IntegerField())),
        unapproved_amount=Sum(Case(When(approved=False, then='amount'), default=0, output_field=DecimalField()))
    )
    # Get top comments with amounts (excluding empty comments)
    top_comments = trxs.exclude(comment='').values('comment').annotate(amount=Sum('amount'), count=Count('id'))
    top_comments = sorted(top_comments, key=lambda x: abs(x['amount'] or 0), reverse=True)[:10]
    return {
        'top_comments': [{
            'comment': item['comment'],
            'amount': round(item['amount'] or 0, 2),
            'count': item['count']
        } for item in top_comments],
        'total_spent': round(totals['total_spent'] or 0, 2),
        'total_income': round(totals['total_income'] or 0, 2),
        'total_amount': round(totals['total_amount'] or 0, 2),
        'uncategorized_count': totals['uncategorized_count'] or 0,
        'uncategorized_amount': round(totals['uncategorized_amount'] or 0, 2),
        'unapproved_count': totals['unapproved_count'] or 0,
        'unapproved_amount': round(totals['unapproved_amount'] or 0, 2),
        'suggested_year_filters': utils.get_suggested_filters(search, 'year'),
        'suggested_month_filters': utils.get_suggested_filters(search, 'month')
    }


@router.post('/import_transactions', response=List[schemas.ImportResponseSchema], exclude_unset=True)
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


# -------------------
# Annual Transactions
# -------------------

@router.get('/annual_transactions', response=schemas.SummarizeCategoriesByMonthSchema, exclude_unset=True)
def annual_transactions(request,
      search: str=Query('', description='Search term to filter transactions')):
    """ Summarize spending by category and month. """
    categories = {c.id:c for c in Category.objects.filter(user=request.user)}
    # Only look at 13 months of data
    mindate = first_of_month(add_months(datetime.now(), -12))
    maxdate = add_months(mindate, 13)
    search = ' '.join([search or '',
        f'date>={mindate.strftime("%Y-%m-%d")}',
        f'date<{maxdate.strftime("%Y-%m-%d")}'])
    searchobj = Search(TRANSACTIONSEARCHFIELDS)
    # Filter the transactions
    trxs = Transaction.objects.filter(user=request.user)
    trxs = searchobj.get_queryset(trxs, search.strip())
    summary = trxs.values('category__id').annotate(month=TruncMonth('date'), saved=Sum('amount'))
    summary = summary.order_by('category__sortid', 'month')
    dates = trxs.aggregate(mindate=Min('date'), maxdate=Max('date'))
    # Build the response object from the django summary
    response = dict(items=[],
        minmonth=first_of_month(dates['mindate']) if dates['mindate'] else None,
        maxmonth=first_of_month(dates['maxdate']) if dates['maxdate'] else None)
    for catid, group in groupby(summary, key=lambda x: x['category__id']):
        cat = categories.get(catid)
        response['items'].append({
            'id': cat.id if cat else None,
            'url': cat.url if cat else None,
            'name': cat.name if cat else 'Uncategorized',
            'exclude': cat.exclude if cat else False,
            'months': {str(row['month']): round(row['saved'] or 0, 2) for row in group},
        })
    return response
