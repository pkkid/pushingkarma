# encoding: utf-8
from datetime import date, datetime
from decimal import Decimal
from ninja import Schema
from typing import List, Optional
from pk.apps.main.schemas import UserSchema


class AccountSchema(Schema):
    url: str
    name: str
    fid: int
    type: str
    payee: str
    balance: Decimal
    balancedt: datetime
    import_rules: Optional[dict] = None


class CategorySchema(Schema):
    url: str
    name: str
    budget: Decimal
    comment: str
    sortindex: int
    exclude_budget: bool


# class TransactionSchema(Schema):
#     user = UserSchema
#     account = AccountSchema
#     trxid = str
#     date = date
#     payee = str
#     category = CategorySchema
#     amount = Decimal
#     approved = bool
#     comment = str
