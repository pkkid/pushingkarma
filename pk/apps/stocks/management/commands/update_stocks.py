#!/usr/bin/env python
# encoding: utf-8
# Update strock values from AlphaVantage
import json, pytz, requests, time
from datetime import datetime, timedelta
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from ...models import FUNCTION, Stock
from pk import log

URL = 'https://www.alphavantage.co/query?function={function}&symbol={ticker}&apikey={apikey}'


class Command(BaseCommand):
    help = __doc__

    def handle(self, *args, **options):
        tz = pytz.timezone(settings.TIME_ZONE)
        now = make_aware(datetime.now())
        expires = now - timedelta(hours=12)
        for stock in Stock.objects.all():
            try:
                modified = stock.modified.astimezone(tz)
                if not stock.history() or stock.modified < expires:
                    url = URL.format(function=FUNCTION, ticker=stock.ticker, apikey=settings.ALPHAVANTAGE_APIKEY)
                    log.info(f'Updating stock {stock.ticker}: {url}')
                    response = requests.get(url)
                    stock.data = json.dumps(response.json())  # validate json
                    stock.save()
                    time.sleep(15)  # Limited to 5/min
                else:
                    timeago = int((now - modified).seconds / 60)
                    log.info(f'Stock {stock.ticker} updated {timeago} minutes ago.')
            except Exception as err:
                log.exception(err)
