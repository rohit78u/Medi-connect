from uuid import UUID
from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_roles
from app.db.session import get_async_db
from app.models.doctor import DoctorProfile
from app.models.user import User

router = APIRouter(prefix="/admin/doctors", tags=["Admin Doctor Verification"])


@router.get("/pending")
async def pending_doctors(
    db: AsyncSession = Depends(get_async_db),
    _: User = Depends(require_roles(["ADMIN"])),
) -> list[dict[str, Any]]:
    result = await db.execute(
        select(DoctorProfile).where(DoctorProfile.is_verified.is_(False))
    )
    return [
        {
            "id": str(doctor.id),
            "user_id": str(doctor.user_id),
            "specialization": doctor.specialization.name if doctor.specialization else None,
            "license_number": doctor.license_number,
            "years_of_experience": doctor.years_of_experience,
            "consultation_fee": float(doctor.consultation_fee),
        }
        for doctor in result.scalars().all()
    ]


@router.post("/{doctor_id}/verify")
async def verify_doctor(
    doctor_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    _: User = Depends(require_roles(["ADMIN"])),
) -> dict[str, Any]:
    doctor = await db.get(DoctorProfile, doctor_id)
    if not doctor:
        from app.exceptions.custom_exceptions import NotFoundException
        raise NotFoundException("Doctor not found")

    doctor.is_verified = True
    await db.commit()
    await db.refresh(doctor)
    return {"id": str(doctor.id), "is_verified": doctor.is_verified}


@router.post("/{doctor_id}/reject")
async def reject_doctor(
    doctor_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    _: User = Depends(require_roles(["ADMIN"])),
) -> dict[str, Any]:
    doctor = await db.get(DoctorProfile, doctor_id)
    if not doctor:
        from app.exceptions.custom_exceptions import NotFoundException
        raise NotFoundException("Doctor not found")

    doctor.is_verified = False
    await db.commit()
    return {"id": str(doctor.id), "is_verified": False, "status": "REJECTED"}
