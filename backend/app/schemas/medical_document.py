import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class MedicalDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: uuid.UUID
    uploaded_by: uuid.UUID
    medical_record_id: uuid.UUID | None = None
    lab_report_id: uuid.UUID | None = None
    original_filename: str
    content_type: str
    file_size: int = Field(ge=1)
    uploaded_at: datetime
