from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.doctor import DoctorProfile
from app.models.medical_record import MedicalRecord
from app.models.patient import PatientProfile
from app.models.prescription import Prescription
from app.models.user import User
from app.schemas.prescription import PrescriptionCreate, PrescriptionResponse

router = APIRouter(prefix="/prescriptions", tags=["prescriptions"])


async def _patient_profile(db: AsyncSession, user_id: uuid.UUID) -> PatientProfile:
    result = await db.execute(select(PatientProfile).where(PatientProfile.user_id == user_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    return profile


async def _doctor_profile(db: AsyncSession, user_id: uuid.UUID) -> DoctorProfile:
    result = await db.execute(select(DoctorProfile).where(DoctorProfile.user_id == user_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    return profile


@router.post("", response_model=PrescriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_prescription(
    payload: PrescriptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doctor = await _doctor_profile(db, current_user.id)
    patient = await db.get(PatientProfile, payload.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    if payload.medical_record_id:
        record = await db.get(MedicalRecord, payload.medical_record_id)
        if not record or record.patient_id != patient.id or record.doctor_id != doctor.id:
            raise HTTPException(status_code=403, detail="Medical record access denied")

    prescription = Prescription(
        **payload.model_dump(),
        doctor_id=doctor.id,
    )
    db.add(prescription)
    await db.commit()
    await db.refresh(prescription)
    return prescription


@router.get("/me", response_model=List[PrescriptionResponse])
async def list_my_prescriptions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    patient = await _patient_profile(db, current_user.id)
    result = await db.execute(
        select(Prescription)
        .where(Prescription.patient_id == patient.id, Prescription.is_active == True)
        .order_by(Prescription.prescribed_date.desc())
    )
    return list(result.scalars().all())
