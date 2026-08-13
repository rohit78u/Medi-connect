import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.payment import PaymentStatus


class PaymentOrderCreate(BaseModel):
    appointment_id: uuid.UUID
    amount: float = Field(..., gt=0.0, example=150.0)
    currency: str = Field(default="INR", max_length=10)


class PaymentVerifyRequest(BaseModel):
    razorpay_order_id: str = Field(..., example="order_K123456789")
    razorpay_payment_id: str = Field(..., example="pay_P987654321")
    razorpay_signature: str = Field(..., example="a1b2c3d4e5f6...")


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    appointment_id: uuid.UUID
    user_id: uuid.UUID
    razorpay_order_id: str
    razorpay_payment_id: Optional[str] = None
    amount: float
    currency: str
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime
