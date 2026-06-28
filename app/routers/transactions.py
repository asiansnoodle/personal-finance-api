from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.schemas.transaction import TransactionResponse, TransactionCreate, TransactionFilter, TransactionUpdate
from app.models.user import User
from app.services.transaction_service import (create_transaction, get_transactions, get_transaction_by_id, update_transaction)

router = APIRouter(
    prefix='/transactions',
    tags=['transactions']
)

@router.post('', response_model=TransactionResponse, status_code=201)
def create_transaction_route(payload: TransactionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_transaction(db, payload, current_user)


@router.get('', response_model=list[TransactionResponse])
def get_transactions_route(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), filters: TransactionFilter = Depends()):
    return get_transactions(db, current_user, filters)


@router.get('/{transaction_id}', response_model=TransactionResponse)
def get_transaction_by_id_route(transaction_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_transaction_by_id(db, transaction_id, current_user)


@router.patch('/{transaction_id}', response_model=TransactionResponse)
def patch_transaction_route(transaction_id: int, payload: TransactionUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return update_transaction(db, transaction_id, payload, current_user)
