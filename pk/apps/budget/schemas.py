# encoding: utf-8
import datetime
from decimal import Decimal
from ninja import Schema
from typing import List, Optional
from pydantic import Field


class AccountSchema(Schema):
    id: Optional[int] = Field(None, description='Internal account id')
    url: str = Field(..., description='URL for the account resource')
    name: str = Field(..., description='Name of this account')
    balance: Optional[Decimal] = Field(None, description='Current balance on the account')
    balance_updated: Optional[datetime.datetime] = Field(None, description='Datetime balance was updated')
    import_rules: Optional[dict] = Field(None, description='Transacation import rules for this account')
    sortid: Optional[int] = Field(None, description='User sort id when listing accounts')


class AccountPatchSchema(Schema):
    name: Optional[str] = Field(..., description='Name of this account')
    import_rules: Optional[dict] = Field(None, description='Transacation import rules for this account')


class CategorySchema(Schema):
    id: Optional[int] = Field(None, description='Internal category id')
    url: str = Field(..., description='URL for the category resource')
    name: str = Field(..., description='Name of this cateogry')
    exclude: Optional[bool] = Field(None, description='Exclude this category from reports')
    sortid: Optional[int] = Field(None, description='User sort id when listing categories')


class CategoryPatchSchema(Schema):
    name: Optional[str] = Field(..., description='Name of this category')


class TransactionSchema(Schema):
    url: str = Field(..., description='URL for the transaction resource')
    trxid: str = Field(..., description='Financial institution transaction id')
    date: datetime.date = Field(..., description='Date of transaction')
    payee: str = Field(..., description='Payee of transaction')
    amount: Decimal = Field(..., description='Amount of transaction')
    approved: bool = Field(..., description='True when user approved transaction')
    comment: Optional[str] = Field(None, description='User comment for transaction')
    account: AccountSchema = Field(..., description='Financial institution of transaction')
    category: Optional[CategorySchema] = Field(None, description='User category of transaction')


class SortSchema(Schema):
    sortlist: List[int] = Field(..., description='List of items ids in sorted order')


class ImportResponseSchema(Schema):
    filename: str = Field(..., description='Filename of imported transactions')
    created: int = Field(..., description='Number of transactions created')
    categorized: int = Field(..., description='Number of transactions categorized')
    mindate: Optional[datetime.date] = Field(None, description='Earliest transaction date')
    maxdate: Optional[datetime.date] = Field(None, description='Latest transaction date')
    safe: bool = Field(..., description='True if using safe import method')
    account: AccountSchema = Field(..., description='Financial institution of transaction')
