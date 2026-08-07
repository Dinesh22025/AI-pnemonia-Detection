"""
Logging configuration for PneumoVision AI.
Provides structured logging with file rotation and console output.
"""

import os
import sys
import logging
import json
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging():
    """
    Configure logging for the application.
    Sets up both console and file handlers with proper formatting.
    """
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    # Log format
    console_format = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    file_format = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_format)
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)

    # File handler (rotating)
    log_file = log_dir / "pneumovision.log"
    file_handler = RotatingFileHandler(
        str(log_file),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
    )
    file_handler.setFormatter(file_format)
    file_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)

    # Error file handler
    error_log_file = log_dir / "error.log"
    error_handler = RotatingFileHandler(
        str(error_log_file),
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
    )
    error_handler.setFormatter(file_format)
    error_handler.setLevel(logging.ERROR)
    root_logger.addHandler(error_handler)

    # Suppress verbose library logging
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("tensorflow").setLevel(logging.ERROR)

    return root_logger
