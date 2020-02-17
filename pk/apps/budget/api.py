# encoding: utf-8
from collections import OrderedDict, defaultdict
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import connection
from django.db.models import Min, Max
from pk import utils
from pk.utils.api import DynamicFieldsSerializer, PartialFieldsSerializer
from pk.utils.context import Bunch
from pk.utils.search import FIELDTYPES, SearchField, Search
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.serializers import SerializerMethodField, ValidationError
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
    
    class Meta:
        model = Account
        fields = ('id','url','name','fid','type','payee','balance','balancedt')


class AccountsViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.order_by('name')
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    list_fields = AccountSerializer.Meta.fields

    def list(self, request, *args, **kwargs):
        accounts = Account.objects.order_by('name')
        page = self.paginate_queryset(accounts)
        serializer = AccountSerializer(page, context={'request':request}, many=True, fields=self.list_fields)
        response = self.get_paginated_response(serializer.data)
        utils.move_to_end(response.data, 'results')
        return response


class CategorySerializer(DynamicFieldsSerializer):
    details = SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id','name','sortindex','budget','comment','url','details')

    def get_details(self, obj):
        request = self.context['request']
        return reverse('category-details', kwargs={'pk':obj.pk}, request=request)


class CategoriesViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.order_by('-sortindex')
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    list_fields = CategorySerializer.Meta.fields

    def list(self, request, *args, **kwargs):
        categories = Category.objects.order_by('sortindex')
        page = self.paginate_queryset(categories)
        serializer = CategorySerializer(page, context={'request':request}, many=True, fields=self.list_fields)
        response = self.get_paginated_response(serializer.data)
        response.data['summary'] = reverse('category-summary', request=request)
        utils.move_to_end(response.data, 'results')
        return response

    @list_route(methods=['get'])
    def summary(self, request, *args, **kwargs):
        summary = CategorySummaryView(request)
        response = self.list(request, *args, **kwargs)
        response.data['total'] = round(sum(float(c['budget']) for c in response.data['results']), 2)
        response.data['summary'] = summary.get_data()
        response.data['results'].append(CATEGORY_NULL)
        for category in response.data['results']:
            category['summary'] = summary.categories[category['name']]
        utils.move_to_end(response.data, 'previous','next','summary','results')
        return response

    @detail_route(methods=['get','patch'])
    def details(self, request, pk, *args, **kwargs):
        # check the month was passed in
        month = request.GET.get('month')
        if month:
            return self.details_month(request, pk, month)
        # return summary for all month
        category = Category.objects.get(pk=pk)
        summary = CategorySummaryView(request, category=category)
        data = CategorySerializer(category, context={'request':request}).data
        data['details'] = OrderedDict(summary.categories[category.name])
        data['details']['num_months'] = summary.data['months']
        for attr in ('mindate','maxdate','average_months','average_mindate','average_maxdate'):
            data['details'][attr] = summary.data[attr]
        utils.move_to_end(data['details'], 'months')
        return Response(data)

    def details_month(self, request, pk, monthstr):
        # check we are patching in notes
        category = Category.objects.get(pk=pk)
        comment = request.data.get('comment')
        if request.method == 'PATCH' and comment is not None:
            self._update_details_month_comment(category, monthstr, comment)
        # return details for the specified monthstr
        data = CategorySerializer(category, context={'request':request}).data
        month = datetime.strptime(monthstr, '%Y-%m-%d').date()
        summary = CategorySummaryView(request, category=category, max_month=month,
            num_months=1, include_transactions=10)
        data['details'] = OrderedDict(summary.categories[category.name])
        data['details'].update(data['details']['months'][0])
        del data['details']['months']
        del data['details']['amount']
        return Response(data)

    def _update_details_month_comment(self, category, monthstr, comment):
        key = '%s:%s' % (monthstr, category.id)
        if comment.strip() == '':
            return KeyValue.objects.filter(key=key).delete()
        KeyValue.objects.update_or_create(key=key, defaults={'value':comment})


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
        category_name = self.context['request'].data.get('category_name')
        if category_name:
            category = utils.get_object_or_none(Category, name__iexact=category_name)
            if not category:
                raise ValidationError("Unknown category '%s'." % category_name)
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
        transactions = Transaction.objects.order_by('-date', 'payee', 'id')
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
        response.data['upload'] = reverse('transaction-upload', request=request)
        utils.move_to_end(response.data, 'previous','next','upload','results')
        return response

    @list_route(methods=['put'], parser_classes=[FormParser, MultiPartParser])
    def upload(self, request, format=None):
        trxmanager = TransactionManager()
        for fileobj in request.FILES.values():
            trxmanager.import_qfx(fileobj.name, fileobj.file)
        return Response(trxmanager.get_status())


class KeyValueSerializer(DynamicFieldsSerializer):
    class Meta:
        model = KeyValue
        fields = ('key','value','url')


class KeyValueViewSet(viewsets.ModelViewSet):
    queryset = KeyValue.objects.order_by('key')
    serializer_class = KeyValueSerializer
    permission_classes = [IsAuthenticated]
    list_fields = KeyValueSerializer.Meta.fields


class CategorySummaryView:

    def __init__(self, request, category=None, max_month=None, num_months=12, include_transactions=0):
        """ Generate a summary view of transactions. Available opts include:
            * max_month (date): max month to include in summary (default current month).
            * num_months (int): num months to include in summary (default 12).
            * include_transactions (int): Set to number of recent transactions to include (default 0).
        """
        today = datetime.today()
        self.data = Bunch()
        self.request = request
        self.category = category
        self.max_month = max_month or date(today.year, today.month, 1)
        self.num_months = num_months
        self.include_transactions = include_transactions
        self.calc_summary()

    def calc_summary(self):
        self.categories = defaultdict()
        self.data.months = self.num_months
        self.data.mindate = self.max_month - relativedelta(months=self.num_months - 1)
        self.data.maxdate = self.max_month + relativedelta(months=1)
        self.data = self._count_transactions(self.data)
        self.data = self._init_total(self.data)
        self.data = self._add_cateogry_months(self.data)
        self.data.totals = sorted(self.data.totals.values(), key=lambda x:x['month'], reverse=REVERSE)
        self.data = self._calc_averages(self.data)

    def get_data(self):
        data = OrderedDict(self.data)
        return utils.move_to_end(data, 'totals')

    def _count_transactions(self, data):
        transactions = Transaction.objects.filter(date__gte=self.data.mindate, date__lt=self.data.maxdate)
        if self.category:
            transactions = transactions.filter(category=self.category)
        self.data.transactions = transactions.count()
        self.data.unapproved = transactions.filter(approved=False).count()
        self.data.uncategorized = transactions.filter(category_id=None).count()
        return data

    def _init_total(self, data):
        """ start the totals category. """
        data.totals = Bunch()
        month = data.mindate
        while month < data.maxdate:
            monthstr = month.strftime(DATEFORMAT)
            data.totals[monthstr] = Bunch()
            data.totals[monthstr].month = monthstr
            data.totals[monthstr].transactions = 0
            data.totals[monthstr].amount = 0.0
            month += relativedelta(months=1)
        return data

    def _add_cateogry_months(self, data):
        """ group data by category, month => amount. """
        lookup = self._summary_query_data(data.mindate, data.maxdate)
        comments = dict(KeyValue.objects.values_list('key', 'value'))
        categories = Category.objects.order_by('sortindex')
        if self.category:
            categories = categories.filter(pk=self.category.pk)
        for category in list(categories) + [None]:
            cdata = Bunch()
            cdata.total = 0.0
            cdata.transactions = 0
            cdata.months = []
            month = data.mindate
            while month < data.maxdate:
                # pull data from lookup dict
                monthstr = month.strftime(DATEFORMAT)
                categoryid = 'null' if category is None else category.id
                key = '%s:%s' % (monthstr, categoryid)
                transactions, amount = lookup.get(key, [0, 0.0])
                # update total data
                data.totals[monthstr].transactions += transactions
                if category and category.name != IGNORED:
                    data.totals[monthstr].amount = round(data.totals[monthstr].amount + amount, 2)
                # update category data
                cdata.transactions += transactions
                cdata.total = round(cdata.total + amount, 2)
                mdata = Bunch()
                mdata.month = monthstr
                mdata.transactions = transactions
                mdata.amount = amount
                mdata.comment = comments.get(key, '')
                mdata.details = '{}?month={}'.format(reverse('category-details',
                    args=[categoryid], request=self.request), monthstr)
                cdata.months.append(mdata)
                # recent transactions
                if self.include_transactions:
                    mdata.recent = self._category_month_transactions(category, month)
                # next month
                month += relativedelta(months=1)
            name = UNCATEGORIZED if category is None else category.name
            self.categories[name] = cdata
            if REVERSE: cdata.months = cdata.months[::-1]
        return data

    def _category_month_transactions(self, category, month):
        monthend = month + relativedelta(months=1)
        transactions = Transaction.objects.filter(date__gte=month, date__lt=monthend)
        transactions = transactions.filter(category=self.category)
        transactions = transactions.select_related('account', 'category')
        transactions = transactions.order_by('-date')[:self.include_transactions]
        serializer = TransactionSerializer(transactions, context={'request':self.request},
            many=True, fields=TransactionsViewSet.list_fields)
        return serializer.data

    def _summary_query_data(self, mindate, maxdate):
        """ Returns a dictionary of {'<categoryid>-<date>': <amount>}. """
        with connection.cursor() as cursor:
            mindatestr = mindate.strftime(DATEFORMAT)
            maxdatestr = maxdate.strftime(DATEFORMAT)
            query = "SELECT printf('%%s:%%s',"
            query += "   substr(datetime(t.date, 'start of month'),0,11),"
            query += "   ifnull(c.id, 'null')) as key,\n"
            query += "  count(t.id) as transactions,\n"
            query += "  round(sum(t.amount), 2) as amount"
            query += " FROM budget_transaction t\n"
            query += " LEFT JOIN budget_category c ON t.category_id = c.id\n"
            query += " WHERE t.date >= %s AND t.date < %s\n"
            if self.category:
                query += "  AND c.name = '%s'\n" % self.category.name
            query += " GROUP BY datetime(t.date, 'start of month'), c.sortindex\n"
            query += " ORDER BY datetime(t.date, 'start of month'), c.sortindex;"
            cursor.execute(query, (mindatestr, maxdatestr))
            return {key:values for key,*values in cursor.fetchall()}

    def _calc_averages(self, data):
        """ update averages accounting for months with incomplete data. """
        # find number of months and daterange to use when calculating average
        start, end = data.mindate, data.maxdate
        query = Transaction.objects.filter(date__gte=data.mindate, date__lt=data.maxdate)
        if query.exists():
            start, end = sorted(query.values('date').aggregate(Min('date'), Max('date')).values())
        if start.day != 1:
            start += relativedelta(months=1)
            start = date(start.year, start.month, 1)
        if (end + relativedelta(days=1)).day != 1:
            end = date(end.year, end.month, 1)
        avg_months = relativedelta(end, start).months
        # Calculate the averages if applicable
        if avg_months:
            data.average_months = avg_months
            data.average_mindate = start
            data.average_maxdate = end
            data.average_total = 0.0
            # calculate the average for each category
            if data.average_months:
                for cdata in self.categories.values():
                    average_total = 0.0
                    for mdata in cdata.months:
                        cdate = datetime.strptime(mdata.month, DATEFORMAT).date()
                        if start <= cdate < end:
                            average_total += mdata.amount
                    cdata.average = round(average_total / float(data.average_months), 2)
                    data.average_total += cdata.average
            data.average_total = round(data.average_total, 2)
        return data
