# encoding: utf-8
# Update strock values from AlphaVantage
import json, logging, pytz, requests, time
from datetime import datetime, timedelta
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from ...models import PROVIDER, Stock
from pk.utils.decorators import log_exception
log = logging.getLogger('cmd')


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument('--ticker', required=False, help='Only update the specified ticker.')

    @log_exception(log)
    def handle(self, *args, **options):
        tz = pytz.timezone(settings.TIME_ZONE)
        now = make_aware(datetime.now())
        expires = now - timedelta(hours=12)
        stocks = Stock.objects.all()
        if options.get('ticker'):
            stocks = stocks.filter(ticker=options['ticker'])
        log.info('--- Updating %s Stocks ---', stocks.count())
        for i, stock in enumerate(stocks):
            try:
                modified = stock.modified.astimezone(tz)
                if not stock.history or stock.modified < expires:
                    if i > 0: time.sleep(60 / PROVIDER.get('limit') + 1)
                    ticker = stock.ticker.replace('.','')
                    url = PROVIDER.get('url').format(ticker=ticker, apikey=PROVIDER.get('apikey'))
                    log.info(f'Updating stock {stock.ticker}: {url}')
                    response = requests.get(url)
                    data = response.json()
                    print('-------------')
                    import pprint; pprint.pprint(data, indent=2)
                    stock.data = json.dumps(data)  # validate json
                    if PROVIDER.get('limitstr') in stock.data:
                        log.warning(f'API Limit Reached? {stock.data}')
                        break
                    stock.save()
                else:
                    timeago = int((now - modified).seconds / 60)
                    log.info(f'Stock {stock.ticker} updated {timeago} minutes ago.')
            except Exception as err:
                log.exception(err)
