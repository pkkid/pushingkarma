# encoding: utf-8
import logging
from django.conf import settings
from django.db import models
from pk.utils.django import TimeStampedModel, ViewModelMixin
from pk.utils.django import reverse
log = logging.getLogger(__name__)


class Account(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, db_index=True)
    balance = models.DecimalField(max_digits=9, decimal_places=2, null=True, default=None)
    balance_updated = models.DateTimeField(null=True, default=None)
    rules = models.JSONField(null=True, default=None)
    sortid = models.IntegerField(default=999)

    def __str__(self):
        name = self.name.lower().replace(' ', '_')[:20]
        return f'<Account {self.id}:{name}>'
    
    @property
    def url(self):
        return reverse('api:account', pk=self.id)


class AccountSummary(models.Model, ViewModelMixin):
    """ DB View aggregates PipeRun pass/fail counts. """
    account = models.OneToOneField(Account, related_name='summary',
        primary_key=True, on_delete=models.DO_NOTHING)
    last_year_transactions = models.IntegerField()
    last_year_spend = models.IntegerField()
    last_year_income = models.IntegerField()
    last_year_saved = models.IntegerField()
    this_year_transactions = models.IntegerField()
    this_year_spend = models.IntegerField()
    this_year_income = models.IntegerField()
    this_year_saved = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'budget_account_summary'

    @classmethod
    def create_sql(cls):
        """ Create the PipeRunSummary view. """
        return f"""
          CREATE VIEW {cls._meta.db_table} AS
          SELECT a.id as account_id,
            COALESCE(COUNT(CASE WHEN t.date >= date('now', 'start of year', '-1 year')
              AND t.date <= date('now', 'start of year') THEN 1 END), 0) AS last_year_transactions,
            COALESCE(ROUND(SUM(CASE WHEN t.date >= date('now', 'start of year', '-1 year')
              AND t.date < date('now', 'start of year') AND t.amount < 0 THEN t.amount END)), 0) AS last_year_spend,
            COALESCE(ROUND(SUM(CASE WHEN t.date >= date('now', 'start of year', '-1 year')
              AND t.date < date('now', 'start of year') AND t.amount > 0 THEN t.amount END)), 0) AS last_year_income,
            COALESCE(ROUND(SUM(CASE WHEN t.date >= date('now', 'start of year', '-1 year')
              AND t.date < date('now', 'start of year') THEN t.amount END)), 0) AS last_year_saved,
            COALESCE(COUNT(CASE WHEN t.date >= date('now', 'start of year') THEN 1 END), 0) AS this_year_transactions,
            COALESCE(ROUND(SUM(CASE WHEN t.date >= date('now', 'start of year') AND t.amount < 0 THEN t.amount END)), 0) AS this_year_spend,
            COALESCE(ROUND(SUM(CASE WHEN t.date >= date('now', 'start of year') AND t.amount > 0 THEN t.amount END)), 0) AS this_year_income,
            COALESCE(ROUND(SUM(CASE WHEN t.date >= date('now', 'start of year') THEN t.amount END)), 0) AS this_year_saved
          FROM budget_account a
          JOIN budget_transaction t ON t.account_id = a.id
          GROUP BY a.id;
        """


class Category(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=True, db_index=True)
    exclude = models.BooleanField(default=False)
    sortid = models.IntegerField(default=999)

    def __str__(self):
        name = self.name.lower().replace(' ', '_')[:20]
        return f'<Category {self.id}:{name}>'
    
    @property
    def url(self):
        return reverse('api:category', pk=self.id)


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
    
    @property
    def url(self):
        return reverse('api:transaction', pk=self.id)
