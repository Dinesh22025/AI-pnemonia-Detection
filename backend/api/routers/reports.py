"""
Reports Router
Handles PDF report generation and downloading.
"""

import logging
import os
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import User, Prediction
from middleware.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/{prediction_id}")
async def download_report(
    prediction_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download PDF report for a specific prediction."""
    prediction = db.query(Prediction).filter(
        Prediction.id == prediction_id,
        Prediction.user_id == current_user.id,
    ).first()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found",
        )
    
    if not prediction.report_pdf or not os.path.exists(prediction.report_pdf):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found. Please re-generate.",
        )
    
    return FileResponse(
        prediction.report_pdf,
        media_type="application/pdf",
        filename=f"pneumovision_report_{prediction_id}.pdf",
    )
