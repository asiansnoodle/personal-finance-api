from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.schemas.transaction import TransactionResponse, TransactionCreate, TransactionFilter, TransactionUpdate
from app.models.transaction import Transaction
from app.models.user import User
from app.models.account import Account

router = APIRouter(
    prefix='/transactions',
    tags=['transactions']
)

@router.post('', response_model=TransactionResponse, status_code=201)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    account = db.query(Account).filter(Account.id == payload.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail='Account does not exist')
    if account.user_id != current_user.id:
        raise HTTPException(status_code=403, detail='Account belongs to another user')

    new_transaction = Transaction(**payload.model_dump())

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction

@router.get('', response_model=list[TransactionResponse])
def get_transactions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), filters: TransactionFilter = Depends()):
    query = db.query(Transaction).join(Account).filter(Account.user_id == current_user.id)

    if filters.category:
        query = query.filter(Transaction.category == filters.category)
    if filters.start_date:
        query = query.filter(Transaction.transaction_date >= filters.start_date)
    if filters.end_date:
        query = query.filter(Transaction.transaction_date <= filters.end_date)
    if filters.account_id:
        query = query.filter(Transaction.account_id == filters.account_id)

    return query.order_by(Transaction.transaction_date.desc()).all()

@router.get('/{transaction_id}', response_model=TransactionResponse)
def get_transaction_by_id(transaction_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    result = db.query(Transaction).filter(Transaction.id == transaction_id).first()

    if not result:
        raise HTTPException(status_code=404, detail='Transaction not found')
    
    if result.account.user_id != current_user.id:
        raise HTTPException(status_code=403, detail='Transaction belongs to another user')
    
    return result

@router.patch('/{transaction_id}', response_model=TransactionResponse)
def patch_transaction_by_id(transaction_id: int, payload: TransactionUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    result = db.query(Transaction).filter(Transaction.id == transaction_id).first()

    if not result:
        raise HTTPException(status_code=404, detail='Transaction not found')
    
    if result.account.user_id != current_user.id:
        raise HTTPException(status_code=403, detail='Transaction belongs to another user')
    
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(result, field, value)
    
    db.commit()
    db.refresh(result)

    return result
