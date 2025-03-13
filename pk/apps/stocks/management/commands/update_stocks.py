# encoding: utf-8
# Update strock values from AlphaVantage
import logging, os
import numpy as np
import yfinance as yf
from decimal import Decimal
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from pk import utils
from pk.apps.stocks.models import Ticker, TickerHistory
from pyrate_limiter import RequestRate, Limiter
from requests import Session
from requests_ratelimiter import LimiterMixin, MemoryQueueBucket

log = logging.getLogger('cmd')
is_none = lambda v: v is None or np.isnan(v)


class CachedLimiterSession(LimiterMixin, Session):
    pass


class Command(BaseCommand):
    help = __doc__
    
    def _download(self, symbols):
        """ Download values from yfinance. """
        log.info(f'Downloading {len(symbols)} tickers from yfinance.')
        session = CachedLimiterSession(
            limiter=Limiter(RequestRate(limit=self.opts['limit'], interval=1)),  # 2/sec
            bucket_class=MemoryQueueBucket)
        ytickers = yf.Tickers(symbols)
        yhistory = yf.download(symbols, period=self.opts['period'], progress=False, session=session)
        return ytickers, yhistory
    
    def _get_info(self, ytickers, symbol):
        """ Return the ticker info from yfinance. """
        try:
            log.debug(f'Fetching info for {symbol}')
            return ytickers.tickers[symbol].info
        except Exception as err:
            log.warning(f'Error fetching info for {symbol}: {err}')
    
    def _create_tickerhistories(self, ytickers, yhistory):
        """ Return a list of TickerHistory objects from the dataframe. """
        log.info('Creating TickerHistory objects.')
        newtickers = []
        newhistories = []
        for symbol in yhistory.columns.levels[1]:
            ticker = Ticker.objects.get(ticker=symbol)
            ticker.info = self._get_info(ytickers, symbol)
            for date, row in yhistory.iterrows():
                if is_none(row['Close'][symbol]): continue
                newhistories.append(TickerHistory(
                    ticker=ticker,
                    date=date,
                    close=Decimal(row['Close'][symbol]),
                    high=Decimal(row['High'][symbol]) if not is_none(row['High'][symbol]) else None,
                    low=Decimal(row['Low'][symbol]) if not is_none(row['Low'][symbol]) else None,
                    volume=int(row['Volume'][symbol]) if not is_none(row['Volume'][symbol]) else None
                ))
            newtickers.append(ticker)
        return newtickers, newhistories

    def save(self, newtickers, newhistories):
        """ Save the TickerHistory objects to the database. """
        with transaction.atomic():
            log.info(f'Saving {len(newtickers)} Ticker objects.')
            Ticker.objects.bulk_create(newtickers, update_conflicts=True,
                update_fields=['info'], unique_fields=['ticker'])
            log.info(f'Saving {len(newhistories)} TickerHistory objects.')
            TickerHistory.objects.bulk_create(newhistories, update_conflicts=True,
                update_fields=['close', 'high', 'low', 'volume'],
                unique_fields=['ticker', 'date'])

    def add_arguments(self, parser):
        parser.add_argument('--loglevel', default='INFO', help='Console log level')
        parser.add_argument('--symbols', help='Only update the specified symbols (csv).')
        parser.add_argument('--period', default='1mo', help='Period 1d,5d,1mo,3mo,6mo,1y,2y,5y,max')
        parser.add_argument('--limit', type=int, default=2, help='Limit requests per second.')

    def handle(self, *args, **opts):
        self.opts = opts
        # Setup logging
        logging.getLogger().setLevel(self.opts['loglevel'])
        basename = os.path.basename(__file__).replace('.py', '')
        utils.update_logging_filepath(f'{settings.LOGDIR}/{basename}.log')
        # Run the script
        symbols = self.opts['symbols'].split(',') if self.opts['symbols'] \
            else list(Ticker.objects.values_list('ticker', flat=True))
        ytickers, yhistory = self._download(symbols)
        newtickers, newhistories = self._create_tickerhistories(ytickers, yhistory)
        self.save(newtickers, newhistories)
