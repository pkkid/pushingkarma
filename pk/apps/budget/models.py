#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from django.db import models, transaction
from django_extensions.db.models import TimeStampedModel
from pk import log, utils
from pk.utils.serializers import DynamicFieldsSerializer


class Category(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    budget = models.DecimalField(max_digits=8, decimal_places=2)
    comment = models.TextField(blank=True, default='')
    sortindex = models.IntegerField(default=None)

    def __init__(self, *args, **kwargs):
        super(Category, self).__init__(*args, **kwargs)
        self._init_sortindex = self.sortindex

    def __str__(self):
        return self.name

    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.sortindex is None:
            categories = Category.objects.order_by('-sortindex')
            self.sortindex = categories[0].sortindex + 1 if categories.exists() else 0
        elif self.sortindex != self._init_sortindex:
            index = 0
            log.info('Moving category %s to index %s', self.name, self.sortindex)
            categories = Category.objects.exclude(id=self.id).order_by('sortindex')
            for catid in categories.values_list('id', flat=True):
                Category.objects.filter(id=catid).update(sortindex=index)
                index += 2 if index == self.sortindex - 1 else 1
        super(Category, self).save(*args, **kwargs)


class CategorySerializer(DynamicFieldsSerializer):
    class Meta:
        model = Category
        fields = ('id','url','name','sortindex','budget','comment')


class CategorySubsetSerializer(DynamicFieldsSerializer):
    class Meta:
        model = Category
        fields = ('url','name','budget')


class Transaction(TimeStampedModel):
    bankid = models.CharField(max_length=255, unique=True, db_index=True)
    account = models.CharField(max_length=255, db_index=True)
    date = models.DateField(db_index=True)
    payee = models.CharField(max_length=255, blank=True, db_index=True)
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL, default=None)
    amount = models.DecimalField(max_digits=8, decimal_places=2, db_index=True)
    approved = models.BooleanField(default=False, db_index=True)
    memo = models.CharField(max_length=255, blank=True, default='')
    comment = models.TextField(blank=True, default='', db_index=True)


class TransactionSerializer(DynamicFieldsSerializer):
    category = CategorySubsetSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = ('id','url','bankid','account','date','payee','category',
            'amount','approved','memo','comment')
