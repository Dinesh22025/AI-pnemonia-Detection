"""
Pydantic schemas for patient management.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PatientCreate(BaseModel):
    """Schema for creating patient profile."""
    age: Optional[int] = Field(None, ge=0, le=150, description="Patient age")
    gender: Optional[str] = Field(None, description="Gender (Male/Female/Other)")
    phone: Optional[str] = Field(None, description="Phone number")
    address: Optional[str] = Field(None, description="Address")
    blood_group: Optional[str] = Field(None, description="Blood group")
    allergies: Optional[str] = Field(None, description="Known allergies")
    medical_history: Optional[str] = Field(None, description="Medical history")

    class Config:
        json_schema_extra = {
            "example": {
                "age": 45,
                "gender": "Male",
                "phone": "+1-555-0123",
                "address": "123 Main St, New York, NY 10001",
                "blood_group": "A+",
                "allergies": "Penicillin",
                "medical_history": "Hypertension",
            }
        }


class PatientUpdate(BaseModel):
    """Schema for updating patient profile."""
    age: Optional[int] = Field(None, ge=0, le=150)
    gender: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    medical_history: Optional[str] = None


class PatientResponse(BaseModel):
    """Schema for patient data response."""
    id: UUID
    user_id: UUID
    age: Optional[int] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    medical_history: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

