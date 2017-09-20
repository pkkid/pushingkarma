#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from pk import utils
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from pk.utils.search import FIELDTYPES, SearchField, Search
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
    queryset = Category.objects.order_by('-order')
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    list_fields = CategorySerializer.Meta.fields

    def list(self, request, *args, **kwargs):
        queryset = Category.objects.order_by('order')
        serializer = CategorySerializer(queryset, context={'request':request},
            many=True, fields=self.list_fields)
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
