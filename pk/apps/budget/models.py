# encoding: utf-8
from django.conf import settings
from django.db import models, transaction
from django_extensions.db.models import TimeStampedModel
from pk import log, utils

ACCOUNT_CHOICES = [('bank','Bank'), ('credit','Credit')]


class Account(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, db_index=True)
    fid = models.IntegerField(null=True, db_index=True)
    type = models.CharField(max_length=255, choices=ACCOUNT_CHOICES)
    payee = models.CharField(max_length=255, blank=True, default='')
    balance = models.DecimalField(max_digits=9, decimal_places=2, null=True, default=None)
    balancedt = models.DateTimeField(null=True, default=None)
    import_rules = utils.JSON5Field(null=True, default=None)

    class Meta:
        unique_together = [['user', 'fid']]


class Category(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=True, db_index=True)
    budget = models.DecimalField(max_digits=8, decimal_places=2)
    comment = models.TextField(blank=True, default='')
    sortindex = models.IntegerField(default=None)
    exclude_budget = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super(Category, self).__init__(*args, **kwargs)
        self._init_sortindex = self.sortindex

    def __str__(self):
        name = self.name.lower().replace(' ', '_')[:20]
        return '%s:%s' % (self.id, name)

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Reorder the categories if needed
        if self.sortindex is None:
            categories = Category.objects.order_by('-sortindex')
            self.sortindex = categories[0].sortindex + 1 if categories.exists() else 0
        elif self.sortindex != self._init_sortindex:
            index = 0
            log.info('Moving category %s to index %s', self.name, self.sortindex)
            categories = Category.objects.exclude(id=self.id).order_by('sortindex')
            self.sortindex = max(0, self.sortindex)
            self.sortindex = min(self.sortindex, len(categories))
            for catid in categories.values_list('id', flat=True):
                index += 1 if index == self.sortindex else 0
                Category.objects.filter(id=catid).update(sortindex=index)
                index += 1
        super(Category, self).save(*args, **kwargs)


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
    # Keep original values
    original_date = models.DateField()
    original_payee = models.CharField(max_length=255, blank=True)
    original_amount = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        unique_together = ('account', 'trxid')

    def __str__(self):
        return '%s:%s:%s:%s' % (self.id, self.account.id, self.trxid, self.payee[:10])
