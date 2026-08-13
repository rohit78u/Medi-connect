import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.appointment import AppointmentStatus
from app.schemas.doctor import DoctorResponse
from app.schemas.patient import PatientResponse


class AppointmentCreate(BaseModel):
    doctor_id: uuid.UUID
    appointment_date: datetime = Field(..., example="2026-09-01T10:00:00Z")
    reason_for_visit: Optional[str] = Field(default=None, example="Routine cardiology checkup")


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus
    clinical_notes: Optional[str] = None


class AppointmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: uuid.UUID
    doctor_id: uuid.UUID
    appointment_date: datetime
    status: AppointmentStatus
    reason_for_visit: Optional[str] = None
    clinical_notes: Optional[str] = None
    patient: PatientResponse
    doctor: DoctorResponse
    created_at: datetime
    updated_at: datetime
