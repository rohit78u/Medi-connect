import uuid
from datetime import date
from typing import Optional
from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class PatientProfile(BaseModel):
    """
    Patient Profile Model linked 1-to-1 with User model.
    """
    __tablename__ = "patient_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    date_of_birth: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True
    )
    gender: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )
    blood_group: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True
    )
    emergency_contact: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )
    medical_history_summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", lazy="selectin")
    appointments: Mapped[list["Appointment"]] = relationship(
        "Appointment",
        back_populates="patient",
        lazy="selectin"
    )
