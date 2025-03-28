# encoding: utf-8
from ninja import Schema
from typing import Optional
from pk import utils


class TickerSchema(Schema):
    # url: str
    ticker: str
    info: Optional[dict] = None
    tags: Optional[str] = None
    # lastday: Optional['TickerHistory'] = None


# class TickerHistory(Schema):
#     ticker = TickerSchema
#     date = date
#     close = Decimal
#     high = Optional[float] = None
#     low = Optional[float] = None
#     volume = Optional[int] = None
