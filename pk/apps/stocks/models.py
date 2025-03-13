# encoding: utf-8
import logging
from django.core.management import call_command
from django.db import models
from django.dispatch import receiver
log = logging.getLogger(__name__)


class Ticker(models.Model):
    ticker = models.CharField(max_length=5, primary_key=True)
    tags = models.CharField(max_length=255, blank=True)
    info = models.JSONField(null=True)

    def __str__(self):
        return f'<Ticker:{self.ticker}:{self.tags.replace(' ',',')}>'


class TickerHistory(models.Model):
    ticker = models.ForeignKey(Ticker, related_name='history', on_delete=models.CASCADE)
    date = models.DateField()
    close = models.DecimalField(max_digits=9, decimal_places=2)
    high = models.DecimalField(max_digits=9, decimal_places=2, null=True)
    low = models.DecimalField(max_digits=9, decimal_places=2, null=True)
    volume = models.IntegerField(null=True)

    class Meta:
        unique_together = ('ticker', 'date')


@receiver(models.signals.post_save, sender=Ticker)
def post_save(sender, instance, created, *args, **kwargs):
    if created:
        log.info(f'Calling Django command: update_stocks --symbols={instance.ticker} --period=1y')
        call_command('update_stocks', symbols=instance.ticker, period='1y')
