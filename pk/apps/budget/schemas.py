# encoding: utf-8
from datetime import date, datetime
from decimal import Decimal
from ninja import Schema
from typing import List, Optional


class AccountSchema(Schema):
    id: Optional[int] = None
    url: str
    name: str
    balance: Optional[Decimal] = None
    balance_updated: Optional[datetime] = None
    import_rules: Optional[dict] = None
    sortid: Optional[int] = None


class CategorySchema(Schema):
    id: Optional[int] = None
    url: str
    name: str
    exclude: Optional[bool] = None
    sortid: Optional[int] = None


class TransactionSchema(Schema):
    url: str
    trxid: str
    date: date
    payee: str
    amount: Decimal
    approved: bool
    comment: Optional[str] = None
    account: AccountSchema
    category: Optional[CategorySchema] = None


class SortSchema(Schema):
    sortlist: List[int]
