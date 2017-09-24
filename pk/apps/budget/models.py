#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from django.db import models, transaction
from django_extensions.db.models import TimeStampedModel
from pk.utils.serializers import DynamicFieldsSerializer


class Category(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    order = models.IntegerField(default=None, unique=True)
    budget = models.DecimalField(max_digits=8, decimal_places=2)
    comment = models.TextField(blank=True, default='')

    def __str__(self):
        return self.name

    @transaction.atomic
    def save(self, *args, **kwargs):
        if not self.order:
            categories = Category.objects.order_by('-order')
            self.order = categories[0].order + 1 if categories.exists() else 0
        super(Category, self).save(*args, **kwargs)


class CategorySerializer(DynamicFieldsSerializer):
    class Meta:
        model = Category
        fields = ('id','url','name','order','budget','comment','created','modified')


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
        fields = ('id','url','bankid','account','date','payee','category',
            'amount','approved','memo','comment','created','modified')
