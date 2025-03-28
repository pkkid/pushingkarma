# encoding: utf-8
from datetime import date
from decimal import Decimal
from ninja import Schema
from typing import Optional


class TickerSchema(Schema):
    url: str
    ticker: str
    tags: Optional[str] = None
    info: Optional[dict] = None
    lastday: Optional['TickerHistory'] = None


class TickerHistory(Schema):
    ticker: Optional[TickerSchema] = None
    date: date
    close: Decimal
    high: Decimal
    low: Decimal
    volume: Decimal
