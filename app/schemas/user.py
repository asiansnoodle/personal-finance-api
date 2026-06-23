from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str | None = None

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None
    
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

# Part B — app/schemas/user.py
# You need three schemas — these are Pydantic models that define what the API accepts and returns (separate from your SQLAlchemy ORM models):

# UserCreate — what the registration endpoint accepts: email: str, password: str, full_name: str | None
# UserResponse — what the API returns after creating a user: id: int, email: str, full_name: str | None. Add model_config = ConfigDict(from_attributes=True) so Pydantic can read SQLAlchemy objects directly
# Token — what the login endpoint returns: access_token: str, token_type: str