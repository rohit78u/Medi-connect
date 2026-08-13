import enum
import uuid
from typing import Optional
from sqlalchemy import Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class PaymentStatus(str, enum.Enum):
    CREATED = "CREATED"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class PaymentTransaction(BaseModel):
    """
    Payment Transaction Model tracking Razorpay consultation checkout sessions.
    """
    __tablename__ = "payment_transactions"

    appointment_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("appointments.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    razorpay_order_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False
    )
    razorpay_payment_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True
    )
    razorpay_signature: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    amount: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )
    currency: Mapped[str] = mapped_column(
        String(10),
        default="INR",
        nullable=False
    )
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus),
        default=PaymentStatus.CREATED,
        nullable=False,
        index=True
    )

    # Relationships
    appointment: Mapped["Appointment"] = relationship("Appointment", lazy="selectin")
    user: Mapped["User"] = relationship("User", lazy="selectin")
