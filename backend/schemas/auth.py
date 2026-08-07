"""
Pydantic schemas for authentication and user management.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class UserCreate(BaseModel):
    """Schema for user registration."""
    name: str = Field(..., min_length=2, max_length=100, description="Full name")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=8, max_length=128, description="Password")
    role: Optional[str] = Field("patient", description="User role (patient/doctor)")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """Validate password strength."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """Validate name."""
        v = v.strip()
        if not v.replace(" ", "").isalpha():
            raise ValueError("Name must contain only letters and spaces")
        return v.title()

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "password": "SecurePass123!",
                "role": "patient",
            }
        }


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., description="Password")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@example.com",
                "password": "SecurePass123!",
            }
        }


class UserResponse(BaseModel):
    """Schema for user data response."""
    id: UUID
    name: str
    email: str
    role: str
    is_active: bool
    is_verified: bool
    profile_image: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

    @staticmethod
    def from_orm(obj):
        """Compatibility wrapper for Pydantic v2."""
        return UserResponse(
            id=obj.id,
            name=obj.name,
            email=obj.email,
            role=obj.role.value if hasattr(obj.role, 'value') else obj.role,
            is_active=obj.is_active,
            is_verified=obj.is_verified,
            profile_image=obj.profile_image,
            created_at=obj.created_at,
        )


class TokenResponse(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIs...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
                "token_type": "bearer",
                "expires_in": 1800,
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "John Doe",
                    "email": "john@example.com",
                    "role": "patient",
                    "is_active": True,
                    "is_verified": True,
                    "created_at": "2024-01-01T00:00:00",
                },
            }
        }


class PasswordChange(BaseModel):
    """Schema for password change request."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v):
        """Validate new password strength."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        return v


class PasswordReset(BaseModel):
    """Schema for password reset request."""
    email: EmailStr = Field(..., description="Email address")
    otp: Optional[str] = Field(None, description="OTP for verification")
    new_password: Optional[str] = Field(None, min_length=8, description="New password")
