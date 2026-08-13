import uuid
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.user import UserResponse


class PatientBase(BaseModel):
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(default=None, max_length=20)
    blood_group: Optional[str] = Field(default=None, max_length=10)
    emergency_contact: Optional[str] = Field(default=None, max_length=20)
    medical_history_summary: Optional[str] = None


class PatientCreate(PatientBase):
    pass


class PatientUpdate(PatientBase):
    pass


class PatientResponse(PatientBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    user: UserResponse
    created_at: datetime
    updated_at: datetime
