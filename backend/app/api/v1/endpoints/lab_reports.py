from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_async_db
from app.models.doctor import DoctorProfile
from app.models.lab_report import LabReport
from app.models.medical_record import MedicalRecord
from app.models.patient import PatientProfile
from app.models.user import User
from app.schemas.lab_report import LabReportCreate, LabReportResponse

router = APIRouter(prefix="/lab-reports", tags=["lab-reports"])


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


@router.post("", response_model=LabReportResponse, status_code=status.HTTP_201_CREATED)
async def create_lab_report(
    payload: LabReportCreate,
    db: AsyncSession = Depends(get_async_db),
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

    report = LabReport(**payload.model_dump(), doctor_id=doctor.id)
    db.add(report)
    await db.flush()
    await db.refresh(report)
    return report


@router.get("/me", response_model=List[LabReportResponse])
async def list_my_lab_reports(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    patient = await _patient_profile(db, current_user.id)
    result = await db.execute(
        select(LabReport)
        .where(LabReport.patient_id == patient.id, LabReport.is_active == True)
        .order_by(LabReport.report_date.desc())
    )
    return list(result.scalars().all())
