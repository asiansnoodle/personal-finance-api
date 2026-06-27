from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.schemas.account import AccountCreate, AccountResponse
from app.models.account import Account
from app.models.user import User
from app.exceptions import FinanceAPIException


router = APIRouter(
    prefix='/accounts',
    tags=['accounts']
)

@router.post('', response_model=AccountResponse, status_code=201)
def create_account(payload: AccountCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    new_account = Account(**payload.model_dump(), user_id=current_user.id)

    db.add(new_account)
    db.commit()
    db.refresh(new_account)

    return new_account

@router.get('', response_model=list[AccountResponse])
def get_all_accounts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    result = db.query(Account).filter(Account.user_id == current_user.id).all()
    return result

@router.get('/{account_id}', response_model=AccountResponse)
def get_one_account(account_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    result = db.query(Account).filter(Account.id == account_id).first()

    if not result:
        raise FinanceAPIException(
            status_code=404,
            error='Not Found',
            detail=f'Account {account_id} not found'
        )
    
    if result.user_id != current_user.id:
        raise FinanceAPIException(
            status_code=403,
            error="Forbidden",
            detail="Account belongs to another user"
        )
    
    return result
