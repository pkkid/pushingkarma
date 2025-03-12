import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from django.db.models import Q, Count, Sum
from django.db.models.functions import TruncMonth
from pk import utils  # noqa
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .manager import TransactionManager
from .models import Transaction

DATEFORMAT = '%Y-%m-%d'


@api_view(['get'])
def budget(request):
    root = reverse('api-root', request=request)
    return Response({
        'budget/accounts': f'{root}budget/accounts',
        'budget/categories': f'{root}budget/categories',
        'budget/summary': f'{root}budget/summary',
        'budget/transactions': f'{root}budget/transactions',
        'budget/upload': f'{root}budget/upload',
    })


@api_view(['get'])
@permission_classes([IsAuthenticated])
def history(request, *args, **kwargs):
    this_year = int(datetime.date.today().year)
    this_month = int(datetime.date.today().month)
    two_years_ago = datetime.date(this_year - 2, 1, 1)
    # Fetch the dataset to use
    data = Transaction.objects.filter(user=request.user)                # Filter to only this user
    data = data.filter(date__gte=two_years_ago)                         # Only get last two years of data
    data = data.exclude(category__exclude_budget=True)                  # Ignore ignored.. :P
    data = data.annotate(month=TruncMonth('date'))                      # Truncate to month and add to select list
    data = data.values('category__name', 'month')                       # Group By month
    data = data.annotate(count=Count('id'), spent=Sum('amount'))        # Select the count of the grouping
    data = data.values('category__name', 'month', 'spent', 'count')     # Select month and count
    # Convert the dataset to a chartable format
    # Category -> Year -> Month
    history = {'Total':{this_year-2:[0]*12, this_year-1:[0]*12, this_year:[0]*this_month}}
    for item in data:
        category = item['category__name']
        year = int(item['month'].strftime('%Y'))
        month = int(item['month'].strftime('%m')) - 1
        # Setup the default data set
        if category not in history: history[category] = {}
        if this_year-2 not in history[category]: history[category][this_year-2] = [0]*12
        if this_year-1 not in history[category]: history[category][this_year-1] = [0]*12
        if this_year not in history[category]: history[category][this_year] = [0]*this_month
        # Add the new data
        history[category][year][month] = round(item['spent'], 2)
        history['Total'][year][month] += round(item['spent'], 2)
    return Response(history)
    

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
        if fileobj.name.lower().endswith('.qfx'):
            trxmanager.import_qfx(request.user, fileobj.name, fileobj.file)
        elif fileobj.name.lower().endswith('.csv'):
            trxmanager.import_csv(request.user, fileobj.name, fileobj.file)
    return Response(trxmanager.get_status())
