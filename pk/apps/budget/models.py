#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from django.db import models
from django_extensions.db.models import TimeStampedModel
from pk.utils.serializers import DynamicFieldsSerializer


class Category(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    budget = models.DecimalField(max_digits=8, decimal_places=2)
    comment = models.TextField(blank=True, default='')


class Transaction(TimeStampedModel):
    bankid = models.CharField(max_length=255, unique=True)
    account = models.CharField(max_length=255)
    date = models.DateField()
    payee = models.CharField(max_length=255, blank=True)
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL, default=None)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    approved = models.BooleanField(default=False)
    memo = models.CharField(max_length=255, blank=True, default='')
    comment = models.TextField(blank=True, default='')


class TransactionSerializer(DynamicFieldsSerializer):
    class Meta:
        model = Transaction
        fields = ('id','url','weburl','title','slug','tags','body','html','created','modified')
