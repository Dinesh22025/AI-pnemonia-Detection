"""
Database Models for PneumoVision AI
SQLAlchemy ORM models for all entities
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Enum,
    JSON,
    UniqueConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .connection import Base


class UserRole(str, PyEnum):
    """User role enumeration."""
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"


class PredictionResult(str, PyEnum):
    """Prediction result enumeration."""
    NORMAL = "Normal"
    PNEUMONIA = "Pneumonia"


class User(Base):
    """User model for authentication and profile management."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.PATIENT, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    profile_image = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="user", uselist=False, cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_user_email_role", "email", "role"),
    )

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class Patient(Base):
    """Patient model for additional medical information."""
    __tablename__ = "patients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(10), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    blood_group = Column(String(5), nullable=True)
    allergies = Column(Text, nullable=True)
    medical_history = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="patient")

    def __repr__(self):
        return f"<Patient {self.user_id}>"


class Prediction(Base):
    """Prediction model for storing X-ray analysis results."""
    __tablename__ = "predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="SET NULL"), nullable=True)
    
    # Image information
    image_path = Column(String(500), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=True)
    image_format = Column(String(10), nullable=True)
    
    # Prediction results
    prediction = Column(Enum(PredictionResult), nullable=False)
    confidence = Column(Float, nullable=False)
    probability_normal = Column(Float, nullable=False)
    probability_pneumonia = Column(Float, nullable=False)
    
    # Model information
    model_version = Column(String(50), nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    
    # Visual results
    gradcam_image = Column(String(500), nullable=True)
    report_pdf = Column(String(500), nullable=True)
    
    # Metadata
    doctor_notes = Column(Text, nullable=True)
    is_reviewed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="predictions")
    patient = relationship("Patient", backref="predictions")

    __table_args__ = (
        Index("idx_prediction_user_created", "user_id", "created_at"),
        Index("idx_prediction_result", "prediction", "confidence"),
    )

    def __repr__(self):
        return f"<Prediction {self.id}: {self.prediction} ({self.confidence:.2%})>"


class Doctor(Base):
    """Doctor model for healthcare professional management."""
    __tablename__ = "doctors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    specialization = Column(String(100), nullable=False)
    license_number = Column(String(50), unique=True, nullable=True)
    phone = Column(String(20), nullable=True)
    hospital = Column(String(200), nullable=True)
    is_available = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Dr. {self.name} ({self.specialization})>"


class AuditLog(Base):
    """Audit log model for tracking system activities."""
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(100), nullable=True)
    resource_id = Column(String(100), nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    status = Column(String(20), default="success", nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    __table_args__ = (
        Index("idx_audit_user_action", "user_id", "action"),
        Index("idx_audit_timestamp", "timestamp"),
    )

    def __repr__(self):
        return f"<AuditLog {self.action} by {self.user_id}>"

