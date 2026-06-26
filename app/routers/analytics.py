from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.analytics import SpendSummary, BudgetVariance
from app.services.analytics_service import get_spend_summary, get_budget_variance

router = APIRouter(
    prefix='/analytics',
    tags=['analytics']
)

@router.get('/summary', response_model=SpendSummary)
def get_summary(month: int = Query(ge=1, le=12), year: int = Query(ge=2000, le=2100), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    summary = get_spend_summary(db, current_user.id, month, year)
    return summary

@router.get('/variance', response_model=list[BudgetVariance])
def get_variance(month: int = Query(ge=1, le=12), year: int = Query(ge=2000, le=2100), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    variance = get_budget_variance(db, current_user.id, month, year)
    return variance


