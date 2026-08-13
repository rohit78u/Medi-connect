import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class MedicalRecord(BaseModel):
    """Clinical record belonging to a patient and authored by a doctor."""

    __tablename__ = "medical_records"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    doctor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("doctor_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    appointment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True, index=True
    )
    record_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    diagnosis: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    symptoms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    clinical_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    treatment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    patient: Mapped["PatientProfile"] = relationship("PatientProfile", lazy="selectin")
    doctor: Mapped["DoctorProfile"] = relationship("DoctorProfile", lazy="selectin")
    appointment: Mapped[Optional["Appointment"]] = relationship("Appointment", lazy="selectin")
