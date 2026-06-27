from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.user import UserCreate, UserResponse, Token
from app.services.auth_service import get_user_by_email, hash_password, verify_password, create_access_token
from app.models.user import User
from app.exceptions import FinanceAPIException

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

@router.post('/register', response_model=UserResponse, status_code=201)
def auth_register(payload: UserCreate, db: Session = Depends(get_db)):

    existing = get_user_by_email(db, payload.email)
    if existing:
        raise FinanceAPIException(
            status_code=400,
            error="Bad Request",
            detail="Email already registered"
        )
            
    hashed = hash_password(payload.password)
    user = User(email=payload.email, hashed_password=hashed, full_name=payload.full_name)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@router.post('/login')
def auth_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise FinanceAPIException(
            status_code=401,
            error="Unauthorized",
            detail="Incorrect email or password"
        )

    token = create_access_token({'sub': user.email})
    return Token(access_token=token, token_type='bearer')

