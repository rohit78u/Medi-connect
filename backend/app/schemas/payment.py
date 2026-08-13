import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.payment import PaymentStatus


class PaymentOrderCreate(BaseModel):
    """Only the appointment is client-controlled; the server calculates the amount."""
    appointment_id: uuid.UUID
    currency: str = Field(default="INR", pattern="^[A-Za-z]{3}$")


class PaymentVerifyRequest(BaseModel):
    razorpay_order_id: str = Field(..., min_length=5, max_length=100)
    razorpay_payment_id: str = Field(..., min_length=5, max_length=100)
    razorpay_signature: str = Field(..., min_length=32, max_length=128)


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    appointment_id: uuid.UUID
    user_id: uuid.UUID
    razorpay_order_id: str
    razorpay_payment_id: str | None = None
    amount: float
    currency: str
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime
