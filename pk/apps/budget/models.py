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
    total_spend = models.IntegerField()
    total_income = models.IntegerField()
    avg_spend_per_month = models.IntegerField()
    avg_income_per_month = models.IntegerField()
    transactions_this_year = models.IntegerField()
    spend_this_year = models.IntegerField()
    income_this_year = models.IntegerField()
    avg_transactions_per_month_this_year = models.IntegerField()
    avg_spend_per_month_this_year = models.IntegerField()
    avg_income_per_month_this_year = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'budget_account_summary'

    @classmethod
    def create_sql(cls):
        """ Create the PipeRunSummary view. """
        return f"""--sql
          CREATE VIEW {cls._meta.db_table} AS
          SELECT a.id as account_id,
            -- Totals
            COUNT(t.id) AS total_transactions,
            ROUND(SUM(CASE WHEN t.amount < 0 THEN t.amount END)) AS total_spend,
            ROUND(SUM(CASE WHEN t.amount > 0 THEN t.amount END)) AS total_income,
            -- Per Month
            ROUND(COUNT(t.id) / 12.0) AS avg_transactions_per_month,
            ROUND(SUM(CASE WHEN t.amount < 0 THEN t.amount END) / 12.0) AS avg_spend_per_month,
            ROUND(SUM(CASE WHEN t.amount > 0 THEN t.amount END) / 12.0) AS avg_income_per_month,
            -- This Year
            COUNT(CASE WHEN t.date >= date('now', 'start of year') THEN 1 END) AS transactions_this_year,
            ROUND(SUM(CASE WHEN t.date >= date('now', 'start of year') AND t.amount < 0 THEN t.amount END)) AS spend_this_year,
            ROUND(SUM(CASE WHEN t.date >= date('now', 'start of year') AND t.amount > 0 THEN t.amount END)) AS income_this_year,
            -- This Year Per Month
            ROUND(COUNT(CASE WHEN t.date >= date('now', 'start of year') THEN 1 END) / (strftime('%m', 'now'))) AS avg_transactions_per_month_this_year,
            ROUND(SUM(CASE WHEN t.date >= date('now', 'start of year') AND t.amount < 0 THEN t.amount END) / (strftime('%m', 'now'))) AS avg_spend_per_month_this_year,
            ROUND(SUM(CASE WHEN t.date >= date('now', 'start of year') AND t.amount > 0 THEN t.amount END) / (strftime('%m', 'now'))) AS avg_income_per_month_this_year
          FROM budget_account a
          JOIN budget_transaction t ON a.id = t.account_id
          WHERE t.date > date('now', '-1 year')
          GROUP BY a.id, a.name;
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
