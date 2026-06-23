from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
from jose import jwt
from datetime import timedelta, datetime, UTC
from app.config import settings
from app.models import User

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain, hashed) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload['exp'] = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    SECRET_KEY = settings.SECRET_KEY
    ALGORITHM = settings.ALGORITHM

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def get_user_by_email(db, email: str):
    return db.query(User).filter(User.email == email).first()
