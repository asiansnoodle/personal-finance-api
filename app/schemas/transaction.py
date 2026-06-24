from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from decimal import Decimal

class TransactionCreate(BaseModel):
    account_id: int
    amount: Decimal
    description: str
    category: str | None = None
    transaction_date: date
    is_income: bool = False

class TransactionResponse(BaseModel):
    id: int
    account_id: int
    amount: Decimal
    description: str
    category: str | None 
    transaction_date: date
    is_income: bool 
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TransactionUpdate(BaseModel):
    account_id: int | None = None
    amount: Decimal | None = None
    description: str | None = None
    category: str | None = None
    transaction_date: date | None = None
    is_income: bool | None = None 

class TransactionFilter(BaseModel):
    category: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    account_id: int | None = None
