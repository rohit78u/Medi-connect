import uuid
from typing import List, Optional
from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Specialization(BaseModel):
    """
    Medical Specialization Model (e.g., Cardiology, Neurology, Pediatrics).
    """
    __tablename__ = "specializations"

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    doctors: Mapped[List["DoctorProfile"]] = relationship(
        "DoctorProfile",
        back_populates="specialization",
        lazy="selectin"
    )


class DoctorProfile(BaseModel):
    """
    Doctor Profile Model linked 1-to-1 with User model.
    """
    __tablename__ = "doctor_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    specialization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("specializations.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    license_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )
    consultation_fee: Mapped[float] = mapped_column(
        Numeric(10, 2),
        default=0.0,
        nullable=False
    )
    years_of_experience: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    bio: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", lazy="selectin")
    specialization: Mapped[Optional[Specialization]] = relationship(
        "Specialization",
        back_populates="doctors",
        lazy="selectin"
    )
    availabilities: Mapped[List["DoctorAvailability"]] = relationship(
        "DoctorAvailability",
        back_populates="doctor",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    appointments: Mapped[List["Appointment"]] = relationship(
        "Appointment",
        back_populates="doctor",
        lazy="selectin"
    )


class DoctorAvailability(BaseModel):
    """
    Doctor Weekly Schedule Availability Slots.
    """
    __tablename__ = "doctor_availabilities"

    doctor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("doctor_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    day_of_week: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="0=Monday, 6=Sunday"
    )
    start_time: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )
    end_time: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    doctor: Mapped[DoctorProfile] = relationship(
        "DoctorProfile",
        back_populates="availabilities"
    )
