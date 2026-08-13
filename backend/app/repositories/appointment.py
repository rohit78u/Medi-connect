import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.appointment import Appointment, AppointmentStatus
from app.repositories.base import BaseRepository


class AppointmentRepository(BaseRepository[Appointment]):
    """
    Repository for Appointment scheduling, double-booking prevention, and state transitions.
    """
    def __init__(self, db: AsyncSession):
        super().__init__(Appointment, db)

    async def get_with_details(self, id: uuid.UUID) -> Optional[Appointment]:
        """
        Fetch appointment by ID with loaded Patient, Doctor, and User relations.
        """
        stmt = (
            select(Appointment)
            .where(Appointment.id == id, Appointment.is_active == True)
            .options(
                selectinload(Appointment.patient),
                selectinload(Appointment.doctor)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def has_doctor_conflict(
        self,
        doctor_id: uuid.UUID,
        appointment_date: datetime,
        exclude_appointment_id: Optional[uuid.UUID] = None
    ) -> bool:
        """
        Check if doctor has an existing PENDING or CONFIRMED appointment at the target date/time.
        Prevents double-booking doctor slots.
        """
        stmt = select(Appointment).where(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == appointment_date,
            Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]),
            Appointment.is_active == True
        )
        if exclude_appointment_id:
            stmt = stmt.where(Appointment.id != exclude_appointment_id)

        result = await self.db.execute(stmt)
        return result.scalars().first() is not None

    async def get_patient_appointments(
        self,
        patient_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[Appointment]:
        """
        Fetch appointments for a given patient.
        """
        stmt = (
            select(Appointment)
            .where(Appointment.patient_id == patient_id, Appointment.is_active == True)
            .options(
                selectinload(Appointment.patient),
                selectinload(Appointment.doctor)
            )
            .order_by(Appointment.appointment_date.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_doctor_appointments(
        self,
        doctor_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[Appointment]:
        """
        Fetch appointments for a given doctor.
        """
        stmt = (
            select(Appointment)
            .where(Appointment.doctor_id == doctor_id, Appointment.is_active == True)
            .options(
                selectinload(Appointment.patient),
                selectinload(Appointment.doctor)
            )
            .order_by(Appointment.appointment_date.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
