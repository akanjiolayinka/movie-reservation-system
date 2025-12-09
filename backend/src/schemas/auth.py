"""
Pydantic schemas for authentication endpoints.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
import uuid

from src.models.user import UserRole


class UserRegisterRequest(BaseModel):
    """Request schema for user registration."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")
    first_name: Optional[str] = Field(None, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, max_length=100, description="Last name")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "securepassword123",
                "first_name": "John",
                "last_name": "Doe"
            }
        }
    )


class UserLoginRequest(BaseModel):
    """Request schema for user login."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }
    )


class TokenResponse(BaseModel):
    """Response schema for authentication tokens."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    )


class UserResponse(BaseModel):
    """Response schema for user data."""
    id: uuid.UUID
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRole
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "role": "user",
                "created_at": "2025-12-09T10:00:00Z"
            }
        }
    )


class UserProfileResponse(BaseModel):
    """Response schema for user profile with additional details."""
    id: uuid.UUID
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: str
    role: UserRole
    is_admin: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
