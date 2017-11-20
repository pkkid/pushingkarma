#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from django.db import models, transaction
from django_extensions.db.models import TimeStampedModel
from pk import log, utils
from pk.utils.serializers import DynamicFieldsSerializer, PartialFieldsSerializer
from rest_framework.serializers import ValidationError

UNCATEGORIZED = 'Uncategorized'
ACCOUNT_CHOICES = [('bank','Bank'), ('credit','Credit')]


class Account(TimeStampedModel):
    name = models.CharField(max_length=255, db_index=True)
    fid = models.IntegerField(unique=True, db_index=True)
    type = models.CharField(max_length=255, choices=ACCOUNT_CHOICES)
    payee = models.CharField(max_length=255, blank=True, default='')
    balance = models.DecimalField(max_digits=9, decimal_places=2, null=True, default=None)
    balancedt = models.DateTimeField(null=True, default=None)


class AccountSerializer(DynamicFieldsSerializer):
    class Meta:
        model = Account
        fields = ('id','url','name','fid','type','payee','balance','balancedt')


class Category(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    budget = models.DecimalField(max_digits=8, decimal_places=2)
    comment = models.TextField(blank=True, default='')
    sortindex = models.IntegerField(default=None)

    def __init__(self, *args, **kwargs):
        super(Category, self).__init__(*args, **kwargs)
        self._init_sortindex = self.sortindex

    def __str__(self):
        name = self.name.lower().replace(' ', '_')[:20]
        return '%s:%s' % (self.id, name)

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Dont allow saving UNCATEGORIZED category
        if self.name == UNCATEGORIZED:
            raise Exception('Cannot modify category %s' % UNCATEGORIZED)
        # reorder the categories if needed
        if self.sortindex is None:
            categories = Category.objects.order_by('-sortindex')
            self.sortindex = categories[0].sortindex + 1 if categories.exists() else 0
        elif self.sortindex != self._init_sortindex:
            index = 0
            log.info('Moving category %s to index %s', self.name, self.sortindex)
            categories = Category.objects.exclude(id=self.id).order_by('sortindex')
            for catid in categories.values_list('id', flat=True):
                index += 1 if index == self.sortindex else 0
                Category.objects.filter(id=catid).update(sortindex=index)
                index += 1
        super(Category, self).save(*args, **kwargs)


class CategorySerializer(DynamicFieldsSerializer):

    class Meta:
        model = Category
        fields = ('id','name','sortindex','budget','comment','url')


class Transaction(TimeStampedModel):
    account = models.ForeignKey(Account)
    trxid = models.CharField(max_length=255, db_index=True)
    date = models.DateField(db_index=True)
    payee = models.CharField(max_length=255, blank=True, db_index=True)
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL, default=None)
    amount = models.DecimalField(max_digits=8, decimal_places=2, db_index=True)
    approved = models.BooleanField(default=False, db_index=True)
    memo = models.CharField(max_length=255, blank=True, default='')
    comment = models.TextField(blank=True, default='', db_index=True)

    class Meta:
        unique_together = ('account', 'trxid')

    def __str__(self):
        return '%s:%s:%s:%s' % (self.id, self.account, self.trxid, self.payee[:10])


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
        if 'category' in self.context['request'].POST:
            category_name = self.context['request'].POST['category']
            category = utils.get_object_or_none(Category, name=category_name)
            if category_name and not category:
                raise ValidationError("Unknown category '%s'." % category_name)
            instance.category = category
        instance.save()
        return instance


class KeyValue(TimeStampedModel):
    key = models.SlugField(primary_key=True, max_length=255, unique=True, null=False)
    value = models.TextField()


class KeyValueSerializer(DynamicFieldsSerializer):
    class Meta:
        model = KeyValue
        fields = ('key','value','url')
