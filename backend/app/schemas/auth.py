from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.schemas.user import UserResponse


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100, example="StrongPassword123!")
    full_name: str = Field(..., min_length=2, max_length=100, example="Dr. Jane Doe")
    phone_number: Optional[str] = Field(default=None, example="+1234567890")
    role_name: str = Field(default="PATIENT", example="DOCTOR")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., example="StrongPassword123!")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str
