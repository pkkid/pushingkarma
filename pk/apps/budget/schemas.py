# encoding: utf-8
from datetime import date, datetime
from decimal import Decimal
from ninja import Schema
from typing import List, Optional
from pydantic import Field


class AccountSchema(Schema):
    id: Optional[int] = Field(None, description='Account id to display')
    url: str = Field(..., description='URL for the account resource')
    name: str = Field(..., description='Name of this account')
    balance: Optional[Decimal] = Field(None, description='Current balance on the account')
    balance_updated: Optional[datetime] = Field(None, description='Datetime balance was updated')
    import_rules: Optional[dict] = Field(None, description='Transacation import rules for this account')
    sortid: Optional[int] = Field(None, description='User sort id when listing accounts')


class AccountPatchSchema(Schema):
    name: Optional[str] = Field(..., description='Name of this account')
    import_rules: Optional[dict] = Field(None, description='Transacation import rules for this account')


class CategorySchema(Schema):
    id: Optional[int] = None
    url: str
    name: str
    exclude: Optional[bool] = None
    sortid: Optional[int] = None


class CategoryPatchSchema(Schema):
    name: Optional[str] = None


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
