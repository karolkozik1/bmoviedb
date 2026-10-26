from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=255)
    password: str = Field(..., min_length=8, max_length=255)
    
class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: EmailStr
    username: str
    role: str
    trust_score: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = Field(default=None, min_length=3, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=255)

class UserRole(str, Enum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=255)
    
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"