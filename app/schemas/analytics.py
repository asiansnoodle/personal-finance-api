from pydantic import BaseModel, ConfigDict
from decimal import Decimal

class CategorySpend(BaseModel):
    category: str
    total: Decimal
    transaction_count: int
    percentage: float

    model_config = ConfigDict(from_attributes=True)

class SpendSummary(BaseModel):
    month: int
    year: int
    total_spend: Decimal
    total_income: Decimal
    net: Decimal
    by_category: list[CategorySpend]

    model_config = ConfigDict(from_attributes=True)

class BudgetVariance(BaseModel):
    category: str
    budgeted: Decimal
    actual: Decimal
    variance: Decimal
    percentage_used: float

    model_config = ConfigDict(from_attributes=True)
