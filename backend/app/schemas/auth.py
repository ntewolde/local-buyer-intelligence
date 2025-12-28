"""
Authentication Schemas
"""
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.models.client import UserRole
import uuid
from datetime import datetime


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data schema"""
    user_id: Optional[str] = None


class UserCreate(BaseModel):
    """User creation schema"""
    email: EmailStr
    password: str
    role: UserRole = UserRole.CLIENT
    client_id: Optional[uuid.UUID] = None


class UserResponse(BaseModel):
    """User response schema"""
    id: uuid.UUID
    email: str
    role: UserRole
    client_id: Optional[uuid.UUID]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
        use_enum_values = True


class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str

