import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class MedicalDocument(BaseModel):
    __tablename__ = "medical_documents"

    patient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    medical_record_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("medical_records.id", ondelete="SET NULL"), nullable=True, index=True)
    lab_report_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("lab_reports.id", ondelete="SET NULL"), nullable=True, index=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    patient = relationship("PatientProfile", lazy="selectin")
    uploader = relationship("User", lazy="selectin")
    medical_record = relationship("MedicalRecord", lazy="selectin")
    lab_report = relationship("LabReport", lazy="selectin")
