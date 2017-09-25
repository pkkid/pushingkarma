#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from pk import log, utils
from pk.utils.search import FIELDTYPES, SearchField, Search
from rest_framework import status, viewsets
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Category, CategorySerializer
from .models import Transaction, TransactionSerializer


TRANSACTIONSEARCHFIELDS = {
    'bankid': SearchField(FIELDTYPES.STR, 'bankid'),
    'account': SearchField(FIELDTYPES.STR, 'account'),
    'date': SearchField(FIELDTYPES.STR, 'date'),
    'payee': SearchField(FIELDTYPES.STR, 'payee'),
    'category': SearchField(FIELDTYPES.STR, 'category'),
    'amount': SearchField(FIELDTYPES.STR, 'amount'),
    'approved': SearchField(FIELDTYPES.STR, 'approved'),
    'memo': SearchField(FIELDTYPES.STR, 'memo'),
    'comment': SearchField(FIELDTYPES.STR, 'comment'),
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
        queryset = Category.objects.order_by('sortindex')
        serializer = CategorySerializer(queryset, context={'request':request},
            many=True, fields=self.list_fields)
        return Response(serializer.data)

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
        return Response(serializer.data)


class TransactionsViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.order_by('-date')
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    list_fields = TransactionSerializer.Meta.fields

    def list(self, request, *args, **kwargs):
        search = request.GET.get('search')
        transactions = Transaction.objects.order_by('-date')
        if search:
            transactions = Search(transactions, TRANSACTIONSEARCHFIELDS, search).queryset()
        serializer = TransactionSerializer(transactions, context={'request':request},
            many=True, fields=self.list_fields)
        return Response(serializer.data)
