import uuid
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class LabReportCreate(BaseModel):
    patient_id: uuid.UUID
    medical_record_id: Optional[uuid.UUID] = None
    test_name: str = Field(min_length=1, max_length=255)
    result: str = Field(min_length=1)
    reference_range: Optional[str] = Field(default=None, max_length=255)
    report_date: date
    notes: Optional[str] = None


class LabReportResponse(LabReportCreate):
    id: uuid.UUID
    doctor_id: Optional[uuid.UUID] = None

    model_config = {"from_attributes": True}
