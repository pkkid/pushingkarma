# encoding: utf-8
from datetime import date, datetime
from decimal import Decimal
from ninja import Schema
from typing import Optional


class AccountSchema(Schema):
    url: str
    name: str
    fid: Optional[int] = None
    payee: Optional[str] = None
    balance: Optional[Decimal] = None
    balancedt: Optional[datetime] = None
    import_rules: Optional[dict] = None


class CategorySchema(Schema):
    url: str
    name: str
    sortindex: Optional[int] = None
    exclude_budget: Optional[bool] = None
    comment: Optional[str] = None


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
