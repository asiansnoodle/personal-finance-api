from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import datetime

class BudgetCreate(BaseModel):
    category: str
    monthly_limit: Decimal
    month: int
    year: int

class BudgetResponse(BaseModel):
    id: int
    user_id: int
    category: str
    monthly_limit: Decimal
    month: int
    year: int 
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class BudgetUpdate(BaseModel):
    category: str | None = None
    monthly_limit: Decimal | None = None
    month: int | None = None
    year: int | None = None
