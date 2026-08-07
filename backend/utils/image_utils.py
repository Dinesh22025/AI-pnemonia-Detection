"""
Image utility functions for validation, preprocessing, and storage.
"""

import os
import uuid
import logging
from pathlib import Path
from typing import Tuple, Optional
from datetime import datetime

import numpy as np
from PIL import Image
from fastapi import UploadFile, HTTPException, status

logger = logging.getLogger(__name__)

# Configuration
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MODEL_INPUT_SIZE = 224

UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


def validate_image(file: UploadFile) -> None:
    """
    Validate uploaded image file.
    
    Args:
        file: Uploaded file to validate
    
    Raises:
        HTTPException: If validation fails
    """
    # Check file extension
    ext = file.filename.split(".")[-1].lower() if file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )
    
    # Check file size
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB",
        )
    
    # Validate image content
    try:
        image = Image.open(file.file)
        image.verify()
        file.file.seek(0)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image file: {str(e)}",
        )


async def save_upload(file: UploadFile) -> Tuple[str, str, int]:
    """
    Save uploaded image to storage.
    
    Args:
        file: Uploaded file
    
    Returns:
        Tuple of (relative_path, original_filename, file_size)
    """
    # Generate unique filename
    ext = file.filename.split(".")[-1].lower()
    unique_filename = f"{uuid.uuid4()}.{ext}"
    
    # Create date-based subdirectory
    date_str = datetime.utcnow().strftime("%Y/%m/%d")
    save_dir = UPLOAD_DIR / date_str
    save_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_path = save_dir / unique_filename
    content = await file.read()
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    relative_path = f"uploads/{date_str}/{unique_filename}"
    logger.info(f"Saved upload: {relative_path} ({len(content)} bytes)")
    
    return relative_path, file.filename, len(content)


def preprocess_image(image_path: str) -> np.ndarray:
    """
    Preprocess image for model inference.
    
    Args:
        image_path: Path to the image file
    
    Returns:
        Preprocessed image array
    """
    try:
        # Load image
        img = Image.open(image_path).convert("RGB")
        
        # Resize to model input size
        img = img.resize((MODEL_INPUT_SIZE, MODEL_INPUT_SIZE), Image.LANCZOS)
        
        # Convert to array and normalize
        img_array = np.array(img, dtype=np.float32) / 255.0
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    except Exception as e:
        logger.error(f"Image preprocessing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image preprocessing failed: {str(e)}",
        )


def generate_thumbnail(image_path: str, size: Tuple[int, int] = (150, 150)) -> str:
    """
    Generate thumbnail for an image.
    
    Args:
        image_path: Path to original image
        size: Thumbnail dimensions
    
    Returns:
        Path to generated thumbnail
    """
    try:
        img = Image.open(image_path)
        img.thumbnail(size, Image.LANCZOS)
        
        thumb_path = image_path.replace(".", "_thumb.")
        img.save(thumb_path, "JPEG", quality=85)
        
        logger.debug(f"Generated thumbnail: {thumb_path}")
        return thumb_path
    except Exception as e:
        logger.error(f"Thumbnail generation error: {str(e)}")
        return image_path


def cleanup_old_files(days: int = 30):
    """
    Clean up uploaded files older than specified days.
    
    Args:
        days: Age threshold in days
    """
    import time
    
    current_time = time.time()
    cutoff = current_time - (days * 86400)
    
    for root, dirs, files in os.walk(UPLOAD_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.getmtime(file_path) < cutoff:
                try:
                    os.remove(file_path)
                    logger.info(f"Cleaned up old file: {file_path}")
                except Exception as e:
                    logger.error(f"Cleanup error for {file_path}: {str(e)}")

