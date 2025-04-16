# encoding: utf-8
import logging
from django.conf import settings
from django.db import models
from pk.utils.django import TimeStampedModel
log = logging.getLogger(__name__)


class Account(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, db_index=True)
    balance = models.DecimalField(max_digits=9, decimal_places=2, null=True, default=None)
    balance_updated = models.DateTimeField(null=True, default=None)
    import_rules = models.JSONField(null=True, default=None)
    sortid = models.IntegerField(default=999)

    def __str__(self):
        name = self.name.lower().replace(' ', '_')[:20]
        return f'<Account {self.id}:{name}>'


class Category(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=True, db_index=True)
    exclude = models.BooleanField(default=False)
    sortid = models.IntegerField(default=999)

    def __str__(self):
        name = self.name.lower().replace(' ', '_')[:20]
        return f'<Category {self.id}:{name}>'


class Transaction(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    trxid = models.CharField(max_length=255, db_index=True)
    date = models.DateField(db_index=True)
    payee = models.CharField(max_length=255, blank=True, db_index=True)
    category = models.ForeignKey(Category, null=True, default=None, on_delete=models.SET_NULL)
    amount = models.DecimalField(max_digits=8, decimal_places=2, db_index=True)
    approved = models.BooleanField(default=False, db_index=True)
    comment = models.TextField(blank=True, default='', db_index=True)
    original_date = models.DateField()
    original_payee = models.CharField(max_length=255, blank=True)
    original_amount = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        unique_together = ('account', 'trxid')

    def __str__(self):
        payee = self.payee.lower().replace(' ', '_')[:10]
        return f'<Transaction {self.id}:{self.trxid}:{payee}>'
