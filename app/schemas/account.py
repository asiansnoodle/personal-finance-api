from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from decimal import Decimal
from app.enums import AccountType


class AccountCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    account_type: AccountType
    balance: Decimal = Decimal("0.00")
    currency: str = Field(default="USD", min_length=3, max_length=3)

class AccountResponse(BaseModel):
    id: int
    user_id: int
    name: str
    account_type: AccountType
    balance: Decimal
    currency: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AccountUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    account_type: AccountType | None = None
    balance: Decimal | None = None
    currency: str | None = Field(default=None, min_length=3, max_length=3)

class AccountSummary(BaseModel):
    id: int
    name: str
    account_type: AccountType
    balance: Decimal

    model_config = ConfigDict(from_attributes=True)
