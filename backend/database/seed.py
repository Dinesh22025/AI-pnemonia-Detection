"""
Database seeding - Creates default admin user and test data.
"""

import logging
from datetime import datetime

from sqlalchemy.orm import Session

from database.models import User, UserRole, Patient, Doctor
from middleware.auth import hash_password

logger = logging.getLogger(__name__)


def seed_admin_user(db: Session) -> None:
    """Create default admin user if not exists."""
    existing = db.query(User).filter(User.email == "admin@pneumovision.ai").first()
    if existing:
        logger.info("Admin user already exists")
        return

    admin = User(
        name="Admin",
        email="admin@pneumovision.ai",
        password_hash=hash_password("Admin@123"),
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True,
    )
    db.add(admin)
    db.commit()
    logger.info("Admin user created: admin@pneumovision.ai / Admin@123")


def seed_test_doctor(db: Session) -> None:
    """Create a test doctor."""
    existing = db.query(Doctor).filter(Doctor.email == "dr.smith@pneumovision.ai").first()
    if existing:
        return

    doctor = Doctor(
        name="Dr. John Smith",
        email="dr.smith@pneumovision.ai",
        specialization="Radiology",
        license_number="MD-12345",
        phone="+1-555-0100",
        hospital="PneumoVision Medical Center",
    )
    db.add(doctor)
    db.commit()
    logger.info("Test doctor created")


def seed_test_patient(db: Session) -> None:
    """Create a test patient user."""
    existing = db.query(User).filter(User.email == "patient@test.com").first()
    if existing:
        return

    from middleware.auth import hash_password

    user = User(
        name="Test Patient",
        email="patient@test.com",
        password_hash=hash_password("Patient@123"),
        role=UserRole.PATIENT,
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    db.flush()

    patient = Patient(
        user_id=user.id,
        age=45,
        gender="Male",
        phone="+1-555-0200",
        address="123 Health Street, Medical City, MC 12345",
        blood_group="O+",
    )
    db.add(patient)
    db.commit()
    logger.info("Test patient created: patient@test.com / Patient@123")
