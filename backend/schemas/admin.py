"""
Pydantic schemas for admin dashboard and management.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class AdminStatsResponse(BaseModel):
    """Schema for admin dashboard statistics."""
    total_users: int
    total_patients: int
    total_predictions: int
    total_doctors: int
    normal_count: int
    pneumonia_count: int
    accuracy: float
    average_confidence: float
    predictions_today: int
    active_users_today: int
    storage_used: str
    monthly_stats: List[Dict[str, Any]]
    model_version: Optional[str] = None
    uptime: str
    last_updated: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "total_users": 150,
                "total_patients": 120,
                "total_predictions": 450,
                "accuracy": 0.98,
                "predictions_today": 12,
            }
        }


class UserManagementResponse(BaseModel):
    """Schema for user management list."""
    id: UUID
    name: str
    email: str
    role: str
    is_active: bool
    is_verified: bool
    predictions_count: int
    last_login: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SystemHealthResponse(BaseModel):
    """Schema for system health status."""
    status: str
    database: str
    model: str
    storage: Dict[str, Any]
    memory_usage: str
    cpu_usage: str
    uptime: str
    version: str
    last_check: datetime

