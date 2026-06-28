from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.models.account import Account
from app.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionFilter, TransactionUpdate
from app.exceptions import FinanceAPIException


def _get_owned_account(db: Session, account_id: int, user_id: int) -> Account:
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise FinanceAPIException(status_code=404, error="Not Found", detail="Account does not exist")
    if account.user_id != user_id:
        raise FinanceAPIException(status_code=403, error="Forbidden", detail="Account belongs to another user")
    return account


def _get_owned_transaction(db: Session, transaction_id: int, user_id: int) -> Transaction:
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise FinanceAPIException(status_code=404, error="Not Found", detail="Transaction not found")
    if transaction.account.user_id != user_id:
        raise FinanceAPIException(status_code=403, error="Forbidden", detail="Transaction belongs to another user")
    return transaction


def create_transaction(db: Session, payload: TransactionCreate, current_user: User) -> Transaction:
    _get_owned_account(db, payload.account_id, current_user.id)
    new_transaction = Transaction(**payload.model_dump())
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return new_transaction


def get_transactions(db: Session, current_user: User, filters: TransactionFilter) -> list[Transaction]:
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


def get_transaction_by_id(db: Session, transaction_id: int, current_user: User) -> Transaction:
    return _get_owned_transaction(db, transaction_id, current_user.id)


def update_transaction(db: Session, transaction_id: int, payload: TransactionUpdate, current_user: User) -> Transaction:
    transaction = _get_owned_transaction(db, transaction_id, current_user.id)
    updates = payload.model_dump(exclude_none=True)
    if "account_id" in updates:
        _get_owned_account(db, updates["account_id"], current_user.id)
    for field, value in updates.items():
        setattr(transaction, field, value)
    db.commit()
    db.refresh(transaction)
    return transaction
