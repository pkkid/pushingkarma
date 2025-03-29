# encoding: utf-8
# Update strock values from AlphaVantage
import logging, os, time
import yfinance as yf
from collections import namedtuple
from concurrent import futures
from decimal import Decimal
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from numpy import isnan
from pk.utils import logging_utils
from pk.apps.stocks.models import Ticker, TickerHistory

log = logging.getLogger(__name__)
YData = namedtuple('YData', ['ticker', 'info', 'history'])


class Command(BaseCommand):
    help = __doc__
    
    def download(self, symbols):
        """ Download values from yfinance. """
        ydata = {}
        log.info(f'Downloading {len(symbols)} tickers from yfinance.')
        with futures.ThreadPoolExecutor(max_workers=self.opts['workers']) as pool:
            promises = {pool.submit(self._download, s):s for s in symbols}
            for future in futures.as_completed(promises):
                symbol = promises[future]
                ydata[symbol] = future.result()
        return ydata
    
    def _download(self, symbol):
        """ Download the dataset from Yahoo Finance. """
        time.sleep(self.opts['delay'])
        log.info(f'Fetching data for {symbol}')
        yticker = yf.Ticker(symbol)
        yinfo = self._info(yticker)
        yhistory = yticker.history(period=self.opts['period'], auto_adjust=True)
        return YData(yticker, yinfo, yhistory)
    
    def _info(self, yticker):
        """ Return the info dictionary from the yfinance object. """
        try:
            yinfo = yticker.info
            del yinfo['companyOfficers']
            return {k:yinfo[k] for k in sorted(yinfo)}
        except Exception as err:
            log.error(f'Error fetching info for {yticker.ticker}; {err}')
            return {}
    
    def create_django_objects(self, ydata):
        """ Return a list of TickerHistory objects from the dataframe. """
        log.info('Creating Ticker and TickerHistory objects.')
        tickers, histories = [], []
        for symbol, data in ydata.items():
            ticker = Ticker(ticker=symbol, info=data.info)
            for date, row in data.history.iterrows():
                if isnan(row['Close']): continue
                history = TickerHistory(
                    ticker=ticker,
                    date=date,
                    close=Decimal(row['Close']),
                    high=Decimal(row['High']) if not isnan(row['High']) else None,
                    low=Decimal(row['Low']) if not isnan(row['Low']) else None,
                    volume=int(row['Volume']) if not isnan(row['Volume']) else None
                )
                ticker.lastday = history
                histories.append(history)
            tickers.append(ticker)
        return tickers, histories

    def save(self, tickers, histories):
        """ Save the TickerHistory objects to the database. """
        with transaction.atomic():
            log.info(f'Saving {len(tickers)} Ticker objects.')
            log.info(f'Saving {len(histories)} TickerHistory objects.')
            TickerHistory.objects.bulk_create(histories, update_conflicts=True,
                update_fields=['close', 'high', 'low', 'volume'],
                unique_fields=['ticker', 'date'])
            Ticker.objects.bulk_create(tickers, update_conflicts=True,
                update_fields=['info', 'lastday'], unique_fields=['ticker'])
            
    def add_arguments(self, parser):
        parser.add_argument('--loglevel', default='INFO', help='Console log level')
        parser.add_argument('--symbols', help='Only update the specified symbols (csv).')
        parser.add_argument('--period', default='13mo', help='Period 1d,5d,1mo,3mo,6mo,1y,2y,5y,max')
        parser.add_argument('--workers', type=int, default=3, help='Max threadpool workers when downloading data.')
        parser.add_argument('--delay', type=int, default=1, help='Delay seconds between workers.')

    def handle(self, *args, **opts):
        self.opts = opts
        # Setup logging
        logging.getLogger().setLevel(self.opts['loglevel'])
        basename = os.path.basename(__file__).replace('.py', '')
        logging_utils.update_logging_filepath(f'{settings.LOGDIR}/{basename}.log')
        # Run the script
        symbols = self.opts['symbols'].split(',') if self.opts['symbols'] \
            else list(Ticker.objects.values_list('ticker', flat=True))
        ydata = self.download(symbols)
        tickers, histories = self.create_django_objects(ydata)
        self.save(tickers, histories)
