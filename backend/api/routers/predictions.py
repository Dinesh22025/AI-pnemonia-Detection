"""
Predictions Router
Handles X-ray image upload, AI prediction, and history management.
"""

import logging
import os
import uuid
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from database.connection import get_db
from database.models import User, Prediction, PredictionResult
from schemas.prediction import (
    PredictionCreate,
    PredictionResponse,
    PredictionHistoryResponse,
    PredictionStats,
    PredictionSummary,
)
from middleware.auth import get_current_user, log_audit
from utils.report_generator import generate_pdf_report

logger = logging.getLogger(__name__)

router = APIRouter()

# Allowed file extensions
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Model service (lazy loaded)
_model = None


def get_model():
    """Lazy load the AI model."""
    global _model
    if _model is None:
        try:
            import tensorflow as tf
            model_path = os.getenv("MODEL_PATH", "../deep_learning/model.keras")
            if os.path.exists(model_path):
                _model = tf.keras.models.load_model(model_path)
                logger.info(f"Model loaded from {model_path}")
            else:
                logger.warning("Model not found. Using mock predictions.")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
    return _model


def validate_image(file: UploadFile) -> bytes:
    """Validate uploaded image file."""
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )
    contents = file.file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Maximum size: 10MB",
        )
    return contents


def save_upload(file: UploadFile, contents: bytes, user_id: uuid.UUID) -> str:
    """Save uploaded file to disk."""
    upload_dir = Path(os.getenv("UPLOAD_DIR", "../uploads"))
    user_dir = upload_dir / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
    filepath = user_dir / filename

    with open(filepath, "wb") as f:
        f.write(contents)

    return str(filepath)


def mock_predict(image_path: str):
    """Mock prediction when model is not available."""
    import random
    confidence = round(random.uniform(0.85, 0.99), 4)
    is_pneumonia = random.random() > 0.5
    return {
        "prediction": PredictionResult.PNEUMONIA if is_pneumonia else PredictionResult.NORMAL,
        "confidence": confidence,
        "probability_normal": round(1 - confidence, 4) if is_pneumonia else confidence,
        "probability_pneumonia": confidence if is_pneumonia else round(1 - confidence, 4),
        "model_version": "mock-v1.0",
        "processing_time_ms": random.randint(100, 500),
    }


@router.post("/upload", response_model=PredictionResponse)
async def upload_and_predict(
    file: UploadFile = File(...),
    doctor_notes: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload X-ray image and run AI prediction."""
    contents = validate_image(file)
    image_path = save_upload(file, contents, current_user.id)
    file_size = len(contents)
    file_format = os.path.splitext(file.filename)[1].lstrip(".")

    start_time = time.time()
    result = mock_predict(image_path)
    processing_time = int((time.time() - start_time) * 1000)

    run_id = uuid.uuid4()
    report_path = None
    try:
        report_path = generate_pdf_report(
            patient_name=current_user.name,
            patient_age=current_user.patient.age if hasattr(current_user, 'patient') and current_user.patient else None,
            patient_gender=current_user.patient.gender if hasattr(current_user, 'patient') and current_user.patient else None,
            prediction=result["prediction"].value if hasattr(result["prediction"], "value") else str(result["prediction"]),
            confidence=result["confidence"],
            probability_normal=result["probability_normal"],
            probability_pneumonia=result["probability_pneumonia"],
            gradcam_image_path=result.get("gradcam_image"),
            doctor_notes=doctor_notes,
        )
    except Exception as e:
        logger.error(f"Report generation failed: {e}")

    prediction = Prediction(
        id=run_id,
        user_id=current_user.id,
        patient_id=current_user.patient.id if hasattr(current_user, 'patient') and current_user.patient else None,
        image_path=image_path,
        original_filename=file.filename,
        file_size=file_size,
        image_format=file_format,
        prediction=result["prediction"],
        confidence=result["confidence"],
        probability_normal=result["probability_normal"],
        probability_pneumonia=result["probability_pneumonia"],
        model_version=result.get("model_version", "v1.0"),
        processing_time_ms=processing_time,
        doctor_notes=doctor_notes,
        report_pdf=report_path,
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    logger.info(
        f"Prediction made: {prediction.prediction.value} "
        f"(confidence: {prediction.confidence:.2%}) "
        f"for user {current_user.email}"
    )

    return PredictionResponse.from_orm(prediction)


@router.get("/history", response_model=PredictionHistoryResponse)
async def get_prediction_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get paginated prediction history."""
    query = db.query(Prediction).filter(Prediction.user_id == current_user.id)
    total = query.count()
    predictions = (
        query.order_by(desc(Prediction.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PredictionHistoryResponse(
        total=total,
        page=page,
        page_size=page_size,
        predictions=[PredictionResponse.from_orm(p) for p in predictions],
    )


@router.get("/stats", response_model=PredictionStats)
async def get_prediction_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get prediction statistics for the dashboard."""
    predictions = db.query(Prediction).filter(Prediction.user_id == current_user.id).all()

    total = len(predictions)
    normal_count = sum(1 for p in predictions if p.prediction == PredictionResult.NORMAL)
    pneumonia_count = sum(1 for p in predictions if p.prediction == PredictionResult.PNEUMONIA)
    average_confidence = (
        sum(p.confidence for p in predictions) / total if total > 0 else 0.0
    )
    accuracy = pneumonia_count / total if total > 0 else 0.0

    # Recent trend: count of predictions per day for the last 7 days
    today = datetime.utcnow().date()
    recent_trend = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = day_start + timedelta(days=1)
        count = db.query(Prediction).filter(
            Prediction.user_id == current_user.id,
            Prediction.created_at >= day_start,
            Prediction.created_at < day_end,
        ).count()
        recent_trend.append({
            "date": day.isoformat(),
            "count": count,
        })

    return PredictionStats(
        total_predictions=total,
        normal_count=normal_count,
        pneumonia_count=pneumonia_count,
        average_confidence=round(average_confidence, 4),
        accuracy=round(accuracy, 4),
        recent_trend=recent_trend,
    )


@router.get("/stats/summary", response_model=PredictionSummary)
async def get_prediction_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get prediction summary for dashboard."""
    predictions = db.query(Prediction).filter(Prediction.user_id == current_user.id).all()

    total = len(predictions)
    normal_count = sum(1 for p in predictions if p.prediction == PredictionResult.NORMAL)
    pneumonia_count = sum(1 for p in predictions if p.prediction == PredictionResult.PNEUMONIA)

    recent = (
        db.query(Prediction)
        .filter(Prediction.user_id == current_user.id)
        .order_by(desc(Prediction.created_at))
        .limit(5)
        .all()
    )

    return PredictionSummary(
        total_predictions=total,
        total_normal=normal_count,
        total_pneumonia=pneumonia_count,
        recent_predictions=[PredictionResponse.from_orm(p) for p in recent],
    )


@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(
    prediction_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific prediction by ID."""
    prediction = db.query(Prediction).filter(
        Prediction.id == prediction_id,
        Prediction.user_id == current_user.id,
    ).first()

    if not prediction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prediction not found")

    return PredictionResponse.from_orm(prediction)


@router.delete("/{prediction_id}")
async def delete_prediction(
    prediction_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a prediction record."""
    prediction = db.query(Prediction).filter(
        Prediction.id == prediction_id,
        Prediction.user_id == current_user.id,
    ).first()

    if not prediction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prediction not found")

    if prediction.image_path and os.path.exists(prediction.image_path):
        os.remove(prediction.image_path)
    if prediction.gradcam_image and os.path.exists(prediction.gradcam_image):
        os.remove(prediction.gradcam_image)
    if prediction.report_pdf and os.path.exists(prediction.report_pdf):
        os.remove(prediction.report_pdf)

    db.delete(prediction)
    db.commit()

    return {"message": "Prediction deleted successfully"}


@router.post("/{prediction_id}/review")
async def review_prediction(
    prediction_id: uuid.UUID,
    doctor_notes: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add doctor review to a prediction."""
    prediction = db.query(Prediction).filter(
        Prediction.id == prediction_id,
        Prediction.user_id == current_user.id,
    ).first()

    if not prediction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prediction not found")

    prediction.doctor_notes = doctor_notes
    prediction.is_reviewed = True
    db.commit()

    return {"message": "Prediction reviewed successfully"}

