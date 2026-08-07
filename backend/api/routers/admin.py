"""
Admin Dashboard Router
Provides analytics, user management, and system statistics.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from database.connection import get_db
from database.models import User, UserRole, Prediction, PredictionResult, AuditLog
from middleware.auth import get_current_user, require_role

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/stats")
async def get_admin_stats(
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db),
):
    """Get comprehensive system statistics for admin dashboard."""
    total_users = db.query(User).count()
    total_patients = db.query(User).filter(User.role == UserRole.PATIENT).count()
    total_doctors = db.query(User).filter(User.role == UserRole.DOCTOR).count()
    total_predictions = db.query(Prediction).count()
    
    normal_count = db.query(Prediction).filter(
        Prediction.prediction == PredictionResult.NORMAL
    ).count()
    pneumonia_count = db.query(Prediction).filter(
        Prediction.prediction == PredictionResult.PNEUMONIA
    ).count()
    
    avg_confidence = db.query(func.avg(Prediction.confidence)).scalar() or 0.0
    
    week_ago = datetime.utcnow() - timedelta(days=7)
    weekly_predictions = db.query(Prediction).filter(
        Prediction.created_at >= week_ago
    ).count()
    weekly_users = db.query(User).filter(
        User.created_at >= week_ago
    ).count()
    
    return {
        "total_users": total_users,
        "total_patients": total_patients,
        "total_doctors": total_doctors,
        "total_predictions": total_predictions,
        "normal_count": normal_count,
        "pneumonia_count": pneumonia_count,
        "average_confidence": float(avg_confidence),
        "weekly_predictions": weekly_predictions,
        "weekly_users": weekly_users,
        "accuracy": pneumonia_count / total_predictions if total_predictions > 0 else 0,
    }


@router.get("/users")
async def get_users(
    page: int = 1,
    page_size: int = 20,
    role: Optional[str] = None,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db),
):
    """Get paginated list of users with optional role filter."""
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    
    total = query.count()
    users_list = query.order_by(desc(User.created_at)) \
                      .offset((page - 1) * page_size) \
                      .limit(page_size) \
                      .all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "users": [{
            "id": str(u.id),
            "name": u.name,
            "email": u.email,
            "role": u.role.value,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat(),
        } for u in users_list],
    }


@router.get("/predictions")
async def get_all_predictions(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db),
):
    """Get all predictions (admin view)."""
    query = db.query(Prediction).order_by(desc(Prediction.created_at))
    total = query.count()
    predictions_list = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "predictions": [{
            "id": str(p.id),
            "user_id": str(p.user_id),
            "prediction": p.prediction.value,
            "confidence": p.confidence,
            "created_at": p.created_at.isoformat(),
        } for p in predictions_list],
    }


@router.put("/users/{user_id}/toggle-status")
async def toggle_user_status(
    user_id: UUID,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db),
):
    """Activate or deactivate a user account."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    user.is_active = not user.is_active
    db.commit()
    
    return {
        "message": f"User {'activated' if user.is_active else 'deactivated'} successfully",
        "is_active": user.is_active,
    }
