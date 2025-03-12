# encoding: utf-8
from django.core.management import call_command
from django.db import models
from django.dispatch import receiver
from pk import log, utils


class Ticker(models.Model):
    ticker = models.CharField(max_length=5, unique=True)
    tags = models.CharField(max_length=255, blank=True)
    info = utils.JSON5Field(null=True)


class TickerHistory(models.Model):
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE)
    date = models.DateField()
    close = models.DecimalField(max_digits=9, decimal_places=2)
    high = models.DecimalField(max_digits=9, decimal_places=2, null=True)
    low = models.DecimalField(max_digits=9, decimal_places=2, null=True)
    volume = models.IntegerField(null=True)


@receiver(models.signals.post_save, sender=Ticker)
def post_save(sender, instance, created, *args, **kwargs):
    if created:
        log.info(f'Calling Django command: updatestocks --ticker={instance.ticker}')
        call_command('update_stocks', ticker=instance.ticker)
