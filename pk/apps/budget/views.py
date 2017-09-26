#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from django.contrib.auth.decorators import login_required
from django.db import transaction
from pk import log, utils
from pk.utils.search import FIELDTYPES, SearchField, Search
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Category, CategorySerializer
from .models import Transaction, TransactionSerializer


TRANSACTIONSEARCHFIELDS = {
    'account': SearchField(FIELDTYPES.STR, 'account'),
    'date': SearchField(FIELDTYPES.DATE, 'date'),
    'payee': SearchField(FIELDTYPES.STR, 'payee'),
    'category': SearchField(FIELDTYPES.STR, 'category__name'),
    'amount': SearchField(FIELDTYPES.NUM, 'amount'),
    'amountstr': SearchField(FIELDTYPES.STR, 'printf("%.2f", amount)'),
    # 'bankid': SearchField(FIELDTYPES.STR, 'bankid'),
    # 'approved': SearchField(FIELDTYPES.STR, 'approved'),
    # 'memo': SearchField(FIELDTYPES.STR, 'memo'),
    # 'comment': SearchField(FIELDTYPES.STR, 'comment'),
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

    @detail_route(methods=['put'])
    @transaction.atomic()
    def sortindex(self, request, *args, **kwargs):
        category = Category.objects.get(id=request.POST['id'])
        sortindex = int(request.POST['sortindex'])
        log.info('Moving category %s to index %s', category.name, sortindex)
        index = 0
        for cat in Category.objects.exclude(id=request.POST['id']).order_by('sortindex'):
            index += 1 if index == sortindex else 0
            utils.update(cat, sortindex=index)
            index += 1
        utils.update(category, sortindex=sortindex)
        serializer = CategorySerializer(category, context={'request':request})
        return Response({'result':serializer.data})


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
