import uuid
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class PrescriptionCreate(BaseModel):
    patient_id: uuid.UUID
    medical_record_id: Optional[uuid.UUID] = None
    medicine_name: str = Field(min_length=1, max_length=255)
    dosage: Optional[str] = Field(default=None, max_length=100)
    frequency: Optional[str] = Field(default=None, max_length=100)
    duration: Optional[str] = Field(default=None, max_length=100)
    instructions: Optional[str] = None
    prescribed_date: date


class PrescriptionResponse(PrescriptionCreate):
    id: uuid.UUID
    doctor_id: uuid.UUID

    model_config = {"from_attributes": True}
