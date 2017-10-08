#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from django.db import models, transaction
from django_extensions.db.models import TimeStampedModel
from rest_framework.serializers import CharField, ValidationError
from pk import log, utils
from pk.utils.serializers import DynamicFieldsSerializer

UNCATEGORIZED = 'Uncategorized'


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
        return '<%s:%s:%s>' % (self.__class__.__name__, self.id, name)

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Dont allow saving Uncategorized category
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
        fields = ('id','url','name','sortindex','budget','comment')


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

    def __str__(self):
        return '<%s:%s:%s:%s>' % (self.__class__.__name__, self.id, self.account, self.bankid)


class TransactionSerializer(DynamicFieldsSerializer):
    category = CharField(source='category.name')

    class Meta:
        model = Transaction
        fields = ('id','url','bankid','account','date','payee','category',
            'amount','approved','memo','comment')

    def validate_category(self, value):
        category = utils.get_object_or_none(Category, name=value)
        if not category:
            raise ValidationError("Unknown category '%s'." % value)
        return value

    def update(self, instance, validated_data):
        for var in ('bankid','account','date','payee','amount','approved','memo','comment'):
            value = validated_data.get(var, getattr(instance, var))
            setattr(instance, var, value)
        instance.category_id = Category.objects.get(name=validated_data['category']['name']).id
        instance.save()
        return instance
