"""
Pydantic schemas for prediction/analysis operations.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class PredictionCreate(BaseModel):
    """Schema for creating a new prediction."""
    patient_id: Optional[UUID] = None
    doctor_notes: Optional[str] = None


class PredictionResponse(BaseModel):
    """Schema for prediction result response."""
    id: UUID
    user_id: UUID
    patient_id: Optional[UUID] = None
    image_path: str
    original_filename: str
    prediction: str
    confidence: float
    probability_normal: float
    probability_pneumonia: float
    gradcam_image: Optional[str] = None
    report_pdf: Optional[str] = None
    doctor_notes: Optional[str] = None
    model_version: Optional[str] = None
    processing_time_ms: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

    @staticmethod
    def from_orm(obj):
        return PredictionResponse(
            id=obj.id,
            user_id=obj.user_id,
            patient_id=obj.patient_id,
            image_path=obj.image_path,
            original_filename=obj.original_filename,
            prediction=obj.prediction.value if hasattr(obj.prediction, 'value') else obj.prediction,
            confidence=obj.confidence,
            probability_normal=obj.probability_normal,
            probability_pneumonia=obj.probability_pneumonia,
            gradcam_image=obj.gradcam_image,
            report_pdf=obj.report_pdf,
            doctor_notes=obj.doctor_notes,
            model_version=obj.model_version,
            processing_time_ms=obj.processing_time_ms,
            created_at=obj.created_at,
        )


class PredictionHistoryResponse(BaseModel):
    """Schema for paginated prediction history."""
    total: int
    page: int
    page_size: int
    predictions: List[PredictionResponse]


class PredictionStats(BaseModel):
    """Schema for prediction statistics."""
    total_predictions: int
    normal_count: int
    pneumonia_count: int
    average_confidence: float
    accuracy: float
    recent_trend: List[dict]


class PredictionSummary(BaseModel):
    """Summary card data for dashboard."""
    total_predictions: int
    total_normal: int
    total_pneumonia: int
    recent_predictions: List[PredictionResponse]
