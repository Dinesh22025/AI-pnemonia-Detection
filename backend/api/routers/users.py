"""
Users Router
Handles user profile management and settings.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import User, UserRole, Patient
from schemas.auth import UserResponse
from middleware.auth import get_current_user, hash_password, verify_password

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile information."""
    return UserResponse.model_validate(current_user)


@router.put("/me")
async def update_profile(
    name: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user's profile."""
    if name:
        current_user.name = name
    db.commit()
    return {"message": "Profile updated successfully"}


@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change current user's password."""
    if not verify_password(current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    current_user.password_hash = hash_password(new_password)
    db.commit()
    return {"message": "Password changed successfully"}
