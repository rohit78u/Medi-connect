import uuid
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: Optional[str] = None


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    phone_number: Optional[str] = Field(default=None, max_length=20)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    role_name: Optional[str] = Field(default="PATIENT", example="PATIENT")


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_verified: bool
    is_active: bool
    is_superuser: bool
    roles: List[RoleResponse] = []
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    phone_number: Optional[str] = Field(default=None, max_length=20)
    password: Optional[str] = Field(default=None, min_length=8, max_length=100)
