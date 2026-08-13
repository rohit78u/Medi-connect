import uuid
from datetime import time
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.custom_exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
)
from app.models.appointment import AppointmentStatus
from app.models.user import User
from app.notifications.celery_tasks import (
    send_appointment_confirmation_email_task,
    send_status_update_email_task,
)
from app.repositories.appointment import AppointmentRepository
from app.repositories.doctor import DoctorRepository
from app.repositories.patient import PatientRepository
from app.schemas.appointment import AppointmentCreate, AppointmentResponse, AppointmentStatusUpdate
from app.websocket.manager import ws_manager


class AppointmentService:
    """Appointment scheduling, availability validation, state transitions and alerts."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.appointment_repo = AppointmentRepository(db)
        self.patient_repo = PatientRepository(db)
        self.doctor_repo = DoctorRepository(db)

    @staticmethod
    def _time_from_value(value: str) -> time:
        """Parse stored HH:MM/HH:MM:SS availability values safely."""
        try:
            parts = [int(part) for part in value.split(":")]
            if len(parts) == 2:
                return time(parts[0], parts[1])
            return time(parts[0], parts[1], parts[2])
        except (ValueError, TypeError, IndexError):
            raise BadRequestException("Doctor availability contains an invalid time.")

    @classmethod
    def _doctor_is_available(cls, doctor, appointment_date) -> bool:
        """Return true only when the requested instant falls inside a weekly slot."""
        weekday = appointment_date.weekday()
        requested_time = appointment_date.timetz().replace(tzinfo=None)
        for slot in doctor.availabilities:
            if slot.day_of_week != weekday:
                continue
            start = cls._time_from_value(slot.start_time)
            end = cls._time_from_value(slot.end_time)
            if start < end and start <= requested_time < end:
                return True
        return False

    async def book_appointment(self, current_user: User, data: AppointmentCreate) -> AppointmentResponse:
        patient = await self.patient_repo.get_by_user_id(current_user.id)
        if not patient:
            patient = await self.patient_repo.create({"user_id": current_user.id})

        doctor = await self.doctor_repo.get_by_id(data.doctor_id)
        if not doctor or not doctor.is_active:
            raise NotFoundException("Target doctor profile does not exist or is inactive.")

        if data.appointment_date <= __import__("datetime").datetime.now(data.appointment_date.tzinfo):
            raise BadRequestException("Appointment must be scheduled for a future date and time.")

        if not doctor.availabilities:
            raise ConflictException("Doctor has not configured any availability slots.")

        if not self._doctor_is_available(doctor, data.appointment_date):
            raise ConflictException("Doctor is not available at the requested date and time.")

        has_conflict = await self.appointment_repo.has_doctor_conflict(
            doctor_id=data.doctor_id,
            appointment_date=data.appointment_date,
        )
        if has_conflict:
            raise ConflictException("Doctor already has a confirmed or pending appointment at the requested date and time.")

        appointment = await self.appointment_repo.create({
            "patient_id": patient.id,
            "doctor_id": data.doctor_id,
            "appointment_date": data.appointment_date,
            "status": AppointmentStatus.PENDING,
            "reason_for_visit": data.reason_for_visit,
        })
        await self.db.commit()

        refetched = await self.appointment_repo.get_with_details(appointment.id)
        response_data = AppointmentResponse.model_validate(refetched)

        send_appointment_confirmation_email_task.delay(
            recipient_email=current_user.email,
            patient_name=current_user.full_name,
            doctor_name=refetched.doctor.user.full_name,
            appointment_date=data.appointment_date.strftime("%Y-%m-%d %H:%M UTC"),
        )
        await ws_manager.send_personal_message(
            message={
                "type": "NEW_APPOINTMENT_BOOKED",
                "appointment_id": str(refetched.id),
                "patient_name": current_user.full_name,
                "appointment_date": data.appointment_date.isoformat(),
            },
            user_id=str(refetched.doctor.user_id),
        )
        return response_data

    async def update_appointment_status(self, current_user: User, appointment_id: uuid.UUID, data: AppointmentStatusUpdate) -> AppointmentResponse:
        appointment = await self.appointment_repo.get_with_details(appointment_id)
        if not appointment:
            raise NotFoundException("Appointment not found.")

        doctor = await self.doctor_repo.get_by_user_id(current_user.id)
        is_assigned_doctor = doctor and doctor.id == appointment.doctor_id
        is_patient = appointment.patient.user_id == current_user.id
        is_admin = current_user.is_superuser or any(r.name == "ADMIN" for r in current_user.roles)
        if not (is_assigned_doctor or is_patient or is_admin):
            raise ForbiddenException("Permission denied to update this appointment.")

        if is_patient and not (is_assigned_doctor or is_admin) and data.status != AppointmentStatus.CANCELLED:
            raise ForbiddenException("Patients are only permitted to cancel their appointments.")

        update_fields = {"status": data.status}
        if data.clinical_notes:
            update_fields["clinical_notes"] = data.clinical_notes
        await self.appointment_repo.update(appointment, update_fields)
        await self.db.commit()

        refetched = await self.appointment_repo.get_with_details(appointment_id)
        response_data = AppointmentResponse.model_validate(refetched)
        send_status_update_email_task.delay(
            recipient_email=refetched.patient.user.email,
            patient_name=refetched.patient.user.full_name,
            status_str=data.status.value,
            clinical_notes=data.clinical_notes,
        )
        await ws_manager.send_personal_message(
            message={
                "type": "APPOINTMENT_STATUS_UPDATED",
                "appointment_id": str(refetched.id),
                "status": data.status.value,
                "clinical_notes": data.clinical_notes,
            },
            user_id=str(refetched.patient.user_id),
        )
        return response_data

    async def get_patient_appointments(self, current_user: User, skip: int = 0, limit: int = 50) -> List[AppointmentResponse]:
        patient = await self.patient_repo.get_by_user_id(current_user.id)
        if not patient:
            return []
        appointments = await self.appointment_repo.get_patient_appointments(patient.id, skip, limit)
        return [AppointmentResponse.model_validate(app) for app in appointments]

    async def get_doctor_appointments(self, current_user: User, skip: int = 0, limit: int = 50) -> List[AppointmentResponse]:
        doctor = await self.doctor_repo.get_by_user_id(current_user.id)
        if not doctor:
            raise NotFoundException("Doctor profile not found for current user.")
        appointments = await self.appointment_repo.get_doctor_appointments(doctor.id, skip, limit)
        return [AppointmentResponse.model_validate(app) for app in appointments]
