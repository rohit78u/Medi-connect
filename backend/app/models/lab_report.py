import uuid
from datetime import date
from typing import Optional

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class LabReport(BaseModel):
    """Structured laboratory result belonging to a patient."""

    __tablename__ = "lab_reports"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    doctor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("doctor_profiles.id", ondelete="SET NULL"), nullable=True, index=True
    )
    medical_record_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("medical_records.id", ondelete="SET NULL"), nullable=True, index=True
    )
    test_name: Mapped[str] = mapped_column(String(255), nullable=False)
    result: Mapped[str] = mapped_column(Text, nullable=False)
    reference_range: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    report_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    patient: Mapped["PatientProfile"] = relationship("PatientProfile", lazy="selectin")
    doctor: Mapped[Optional["DoctorProfile"]] = relationship("DoctorProfile", lazy="selectin")
    medical_record: Mapped[Optional["MedicalRecord"]] = relationship("MedicalRecord", lazy="selectin")
