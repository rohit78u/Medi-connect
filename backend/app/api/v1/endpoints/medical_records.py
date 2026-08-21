import uuid
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_roles
from app.db.session import get_async_db
from app.exceptions.custom_exceptions import ForbiddenException, NotFoundException
from app.models.appointment import Appointment
from app.models.doctor import DoctorProfile
from app.models.medical_record import MedicalRecord
from app.models.patient import PatientProfile
from app.models.user import User
from app.schemas.medical_record import MedicalRecordCreate, MedicalRecordResponse
from app.schemas.response import APIResponse

router = APIRouter(prefix="/medical-records", tags=["Medical Records"])


async def _patient_for_user(db: AsyncSession, user_id: uuid.UUID) -> PatientProfile:
    result = await db.execute(select(PatientProfile).where(PatientProfile.user_id == user_id))
    patient = result.scalars().first()
    if not patient:
        raise NotFoundException("Patient profile not found")
    return patient


async def _doctor_for_user(db: AsyncSession, user_id: uuid.UUID) -> DoctorProfile:
    result = await db.execute(select(DoctorProfile).where(DoctorProfile.user_id == user_id))
    doctor = result.scalars().first()
    if not doctor:
        raise NotFoundException("Doctor profile not found")
    return doctor


@router.post("", response_model=APIResponse[MedicalRecordResponse], status_code=status.HTTP_201_CREATED)
async def create_medical_record(
    payload: MedicalRecordCreate,
    current_user: User = Depends(require_roles(["DOCTOR", "ADMIN"])),
    db: AsyncSession = Depends(get_async_db),
):
    patient_result = await db.execute(select(PatientProfile).where(PatientProfile.id == payload.patient_id))
    patient = patient_result.scalars().first()
    if not patient:
        raise NotFoundException("Patient profile not found")

    if current_user.is_superuser or any(role.name.upper() == "ADMIN" for role in current_user.roles):
        doctor_result = await db.execute(select(DoctorProfile).where(DoctorProfile.user_id == current_user.id))
        doctor = doctor_result.scalars().first()
        if not doctor:
            raise NotFoundException("Doctor profile not found")
    else:
        doctor = await _doctor_for_user(db, current_user.id)

    if payload.appointment_id:
        appointment_result = await db.execute(
            select(Appointment).where(Appointment.id == payload.appointment_id)
        )
        appointment = appointment_result.scalars().first()
        if not appointment:
            raise NotFoundException("Appointment not found")
        if appointment.patient_id != patient.id or appointment.doctor_id != doctor.id:
            raise ForbiddenException("Appointment does not belong to this patient and doctor")

    record = MedicalRecord(
        patient_id=patient.id,
        doctor_id=doctor.id,
        appointment_id=payload.appointment_id,
        record_date=payload.record_date,
        diagnosis=payload.diagnosis,
        symptoms=payload.symptoms,
        clinical_notes=payload.clinical_notes,
        treatment=payload.treatment,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return APIResponse(success=True, message="Medical record created", data=record)


@router.get("/me", response_model=APIResponse[List[MedicalRecordResponse]])
async def get_my_medical_records(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    roles = {role.name.upper() for role in current_user.roles}
    if "PATIENT" in roles:
        patient = await _patient_for_user(db, current_user.id)
        result = await db.execute(
            select(MedicalRecord)
            .where(MedicalRecord.patient_id == patient.id, MedicalRecord.is_active.is_(True))
            .order_by(MedicalRecord.record_date.desc())
        )
    elif "DOCTOR" in roles:
        doctor = await _doctor_for_user(db, current_user.id)
        result = await db.execute(
            select(MedicalRecord)
            .where(MedicalRecord.doctor_id == doctor.id, MedicalRecord.is_active.is_(True))
            .order_by(MedicalRecord.record_date.desc())
        )
    elif "ADMIN" in roles or current_user.is_superuser:
        result = await db.execute(
            select(MedicalRecord)
            .where(MedicalRecord.is_active.is_(True))
            .order_by(MedicalRecord.record_date.desc())
        )
    else:
        raise ForbiddenException("Medical record access denied")

    return APIResponse(success=True, message="Medical records retrieved", data=list(result.scalars().all()))
