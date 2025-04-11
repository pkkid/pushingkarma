# encoding: utf-8
import datetime
from decimal import Decimal
from ninja import Schema
from typing import List, Optional
from pydantic import Field


class TickerSchema(Schema):
    url: str = Field(..., description='URL for the ticker resource')
    ticker: str = Field(..., description='Ticker symbol for this stock')
    tags: Optional[str] = Field(None, description='User tags for this ticker')
    info: Optional[dict] = Field(None, description='Yahoo finance info for this ticker')
    lastday: Optional['TickerHistory'] = Field(None, description='Last day ticker history')


class TickerHistory(Schema):
    ticker: Optional[TickerSchema] = Field(None, description='Ticker symbol for this stock')
    date: datetime.date = Field(..., description='Date of this ticker history')
    close: Decimal = Field(..., description='Closing price of this ticker and date')
    high: Decimal = Field(..., description='High price of this ticker and date')
    low: Decimal = Field(..., description='Low price of this ticker and date')
    volume: Decimal = Field(..., description='Trade volume of this ticker and date')


class DatasetsSchema(Schema):
    labels: List[str] = Field(..., description='Labels for the datasets')
    datasets: List[dict] = Field(..., description='List of datasets to plot')
