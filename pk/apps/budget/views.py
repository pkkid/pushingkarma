#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from pk.utils.search import FIELDTYPES, SearchField, Search
from . import serializers
from .models import Transaction

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


class TransactionsViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.order_by('-date')
    serializer_class = serializers.TransactionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    list_fields = ['id','url','weburl','title','tags','created','modified']

    def list(self, request, *args, **kwargs):
        search = request.GET.get('search')
        transactions = Transaction.objects.order_by('-date')
        if search:
            transactions = Search(transactions, TRANSACTIONSEARCHFIELDS, search).queryset()
        serializer = serializers.TransactionSerializer(transactions, context={'request':request},
            many=True, fields=self.list_fields)
        return Response(serializer.data)
