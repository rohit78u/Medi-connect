import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.user import UserResponse


class SpecializationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: Optional[str] = None


class AvailabilitySlotCreate(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6, example=0)
    start_time: str = Field(..., example="09:00")
    end_time: str = Field(..., example="17:00")


class AvailabilitySlotResponse(AvailabilitySlotCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    doctor_id: uuid.UUID


class DoctorCreate(BaseModel):
    specialization_name: str = Field(..., example="Cardiology")
    license_number: str = Field(..., example="LIC-123456")
    consultation_fee: float = Field(default=100.0, ge=0.0)
    years_of_experience: int = Field(default=5, ge=0)
    bio: Optional[str] = None


class DoctorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    license_number: str
    consultation_fee: float
    years_of_experience: int
    bio: Optional[str] = None
    is_verified: bool
    user: UserResponse
    specialization: Optional[SpecializationResponse] = None
    availabilities: List[AvailabilitySlotResponse] = []
    created_at: datetime
    updated_at: datetime
