from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.dependencies import get_db, get_current_user
from app.schemas.budget import BudgetCreate, BudgetResponse, BudgetUpdate
from app.models.user import User
from app.models.budget import Budget
from app.exceptions import FinanceAPIException

router = APIRouter(
    prefix='/budgets',
    tags=['budgets']
)

@router.post('/', response_model=BudgetResponse, status_code=201)
def post_budget(payload: BudgetCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    budget = Budget(**payload.model_dump(), user_id = current_user.id)

    try:
        db.add(budget)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise FinanceAPIException(
            status_code=400,
            error="Bad Request",
            detail="Budget for this category and period already exists"
        )
    
    db.refresh(budget)
    return budget

@router.get('/', response_model=list[BudgetResponse])
def get_budgets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), month: int | None = None, year: int | None = None):

    query = db.query(Budget).filter(Budget.user_id == current_user.id)

    if month:
        query = query.filter(Budget.month == month)
    if year:
        query = query.filter(Budget.year == year)
    
    return query.all()

@router.get('/{budget_id}', response_model=BudgetResponse)
def get_budget_by_id(budget_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    result = db.query(Budget).filter(Budget.id == budget_id).first()

    if not result:
        raise FinanceAPIException(
            status_code=404,
            error="Not Found",
            detail="Budget not found"
        )
    
    if result.user_id != current_user.id:
        raise FinanceAPIException(
            status_code=403,
            error="Forbidden",
            detail="Budget belongs to another user"
        )
    
    return result

@router.patch('/{budget_id}', response_model=BudgetResponse)
def patch_budget_by_id(budget_id: int, payload: BudgetUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    result = db.query(Budget).filter(Budget.id == budget_id).first()

    if not result:
        raise FinanceAPIException(
            status_code=404,
            error="Not Found",
            detail="Budget not found"
        )
    
    if result.user_id != current_user.id:
        raise FinanceAPIException(
            status_code=403,
            error="Forbidden",
            detail="Budget belongs to another user"
        )
    
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(result, field, value)

    try: 
        db.commit()
    except IntegrityError:
        db.rollback()
        raise FinanceAPIException(
            status_code=400,
            error="Bad Request",
            detail="Budget for this category and period already exists"
        )
    
    db.refresh(result)
    return result
