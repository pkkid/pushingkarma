#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.models import Min, Max
from pk import utils
from pk.utils.context import OrderedBunch
from pk.utils.search import FIELDTYPES, SearchField, Search
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Category, CategorySerializer
from .models import Transaction, TransactionSerializer

DATEFORMAT = '%Y-%m-%d'
TRANSACTIONSEARCHFIELDS = {
    'bank': SearchField(FIELDTYPES.STR, 'account'),
    'date': SearchField(FIELDTYPES.DATE, 'date'),
    'payee': SearchField(FIELDTYPES.STR, 'payee'),
    'category': SearchField(FIELDTYPES.STR, 'category__name'),
    'amount': SearchField(FIELDTYPES.NUM, 'amount'),
    'approved': SearchField(FIELDTYPES.STR, 'approved'),
    'comment': SearchField(FIELDTYPES.STR, 'comment'),
    # 'bankid': SearchField(FIELDTYPES.STR, 'bankid'),
    # 'memo': SearchField(FIELDTYPES.STR, 'memo'),
}


@login_required
def budget(request, slug=None, tmpl='budget.html'):
    data = utils.context.core(request, menuitem='budget')
    return utils.response(request, tmpl, data)


class CategoriesViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.order_by('-sortindex')
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    list_fields = CategorySerializer.Meta.fields

    def list(self, request, *args, **kwargs):
        categories = Category.objects.order_by('sortindex')
        page = self.paginate_queryset(categories)
        serializer = CategorySerializer(page, context={'request':request},
            many=True, fields=self.list_fields)
        return self.get_paginated_response(serializer.data)


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
            searchdata = {'searchstr':searchstr, 'errors':search.errors, 'datefilters': search.datefilters}
        page = self.paginate_queryset(transactions)
        serializer = TransactionSerializer(page, context={'request':request}, many=True, fields=self.list_fields)
        response = self.get_paginated_response(serializer.data)
        response.data.update(searchdata)
        response.data.move_to_end('results')
        return response

    @list_route(methods=['get'])
    def summary(self, request, *args, **kwargs):
        data = OrderedBunch()
        maxdate = datetime.today()
        maxmonth = date(maxdate.year, maxdate.month, 1)
        # initialize data response
        data.months = 12
        data.mindate = maxmonth - relativedelta(months=data.months - 1)
        data.maxdate = maxmonth + relativedelta(months=1)
        # populate summary data
        self._init_summary_total(data)
        self._add_cateogry_values(data)
        self._calc_category_averages(data)
        data.move_to_end('total')
        data.move_to_end('categories')
        return Response(data)

    def _init_summary_total(self, data):
        """ start the totals category. """
        data.total = OrderedBunch()
        for category in Category.objects.all():
            month = data.mindate
            while month < data.maxdate:
                monthstr = month.strftime(DATEFORMAT)
                data.total[monthstr] = 0.0
                month += relativedelta(months=1)

    def _add_cateogry_values(self, data):
        """ group data by category, month => amount. """
        data.categories = []
        lookup = self._get_summary_data(data.mindate, data.maxdate)
        for category in list(Category.objects.order_by('sortindex')) + [None]:
            cdata = OrderedBunch()
            cdata.name = 'Uncategorized' if category is None else category.name
            cdata.total = 0.0
            cdata.average = 0.0
            cdata.amounts = OrderedBunch()
            month = data.mindate
            while month < data.maxdate:
                categoryid = 'null' if category is None else category.id
                monthstr = month.strftime(DATEFORMAT)
                hash = '%s-%s' % (categoryid, monthstr)
                value = lookup.get(hash, 0.0)
                cdata.amounts[monthstr] = value
                cdata.total = round(cdata.total + value, 2)
                data.total[monthstr] = round(data.total[monthstr] + value, 2)
                month += relativedelta(months=1)
            data.categories.append(cdata)

    def _get_summary_data(self, mindate, maxdate):
        """ Returns a dictionary of {'<categoryid>-<date>': <amount>}. """
        with connection.cursor() as cursor:
            mindatestr = mindate.strftime(DATEFORMAT)
            maxdatestr = maxdate.strftime(DATEFORMAT)
            query = "SELECT printf('%%s-%%s', ifnull(c.id, 'null'),"
            query += "  substr(datetime(t.date, 'start of month'),0,11)) as key,\n"
            query += " round(sum(t.amount), 2) as amount FROM budget_transaction t\n"
            query += " LEFT JOIN budget_category c ON t.category_id = c.id\n"
            query += " WHERE t.date >= %s AND t.date < %s\n"
            query += " GROUP BY datetime(t.date, 'start of month'), c.sortindex\n"
            query += " ORDER BY datetime(t.date, 'start of month'), c.sortindex;"
            cursor.execute(query, (mindatestr, maxdatestr))
            return dict(cursor.fetchall())

    def _calc_category_averages(self, data):
        """ update averages accounting for months with incomplete data. """
        # find number of months and daterange to use when calculating average
        query = Transaction.objects.filter(date__gte=data.mindate, date__lt=data.maxdate)
        start, end = sorted(query.values('date').aggregate(Min('date'), Max('date')).values())
        if start.day != 1:
            start += relativedelta(months=1)
            start = date(start.year, start.month, 1)
        if (end + relativedelta(days=1)).day != 1:
            end = date(end.year, end.month, 1)
        data.avg_months = relativedelta(end, start).months
        data.avg_mindate = start
        data.avg_maxdate = end
        # calculate the average for each category
        if data.avg_months:
            for category in data.categories:
                avg_total = 0.0
                for datestr, value in category.amounts.items():
                    cdate = datetime.strptime(datestr, DATEFORMAT).date()
                    if start <= cdate < end:
                        avg_total += value
                category.average = round(avg_total / float(data.avg_months), 2)
