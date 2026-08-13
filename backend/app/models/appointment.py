import enum
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class AppointmentStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Appointment(BaseModel):
    """
    Appointment Model linking Patients with Doctors.
    """
    __tablename__ = "appointments"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("patient_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    doctor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("doctor_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    appointment_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus),
        default=AppointmentStatus.PENDING,
        nullable=False,
        index=True
    )
    reason_for_visit: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    clinical_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    # Relationships
    patient: Mapped["PatientProfile"] = relationship(
        "PatientProfile",
        back_populates="appointments",
        lazy="selectin"
    )
    doctor: Mapped["DoctorProfile"] = relationship(
        "DoctorProfile",
        back_populates="appointments",
        lazy="selectin"
    )
