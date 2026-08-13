import uuid
from datetime import date
from typing import Optional

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Prescription(BaseModel):
    """Medication prescribed by a doctor to a patient."""

    __tablename__ = "prescriptions"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    doctor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("doctor_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    medical_record_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("medical_records.id", ondelete="SET NULL"), nullable=True, index=True
    )
    medicine_name: Mapped[str] = mapped_column(String(255), nullable=False)
    dosage: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    frequency: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    duration: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prescribed_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    patient: Mapped["PatientProfile"] = relationship("PatientProfile", lazy="selectin")
    doctor: Mapped["DoctorProfile"] = relationship("DoctorProfile", lazy="selectin")
    medical_record: Mapped[Optional["MedicalRecord"]] = relationship("MedicalRecord", lazy="selectin")
