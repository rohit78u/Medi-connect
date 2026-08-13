import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class MedicalRecordCreate(BaseModel):
    patient_id: uuid.UUID
    appointment_id: Optional[uuid.UUID] = None
    record_date: datetime
    diagnosis: Optional[str] = Field(default=None, max_length=500)
    symptoms: Optional[str] = None
    clinical_notes: Optional[str] = None
    treatment: Optional[str] = None


class MedicalRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: uuid.UUID
    doctor_id: uuid.UUID
    appointment_id: Optional[uuid.UUID]
    record_date: datetime
    diagnosis: Optional[str]
    symptoms: Optional[str]
    clinical_notes: Optional[str]
    treatment: Optional[str]
