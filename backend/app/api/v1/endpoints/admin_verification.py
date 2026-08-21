from uuid import UUID
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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
        select(DoctorProfile)
        .where(DoctorProfile.is_verified.is_(False))
        .options(selectinload(DoctorProfile.user), selectinload(DoctorProfile.specialization))
    )
    return [
        {
            "id": str(doctor.id),
            "user_id": str(doctor.user_id),
            "full_name": doctor.user.full_name if doctor.user else None,
            "email": doctor.user.email if doctor.user else None,
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

    # Doctor search requires both the clinical profile and its linked user
    # to be verified. The previous implementation only flipped the profile
    # flag, so an approved doctor could remain invisible to patients.
    user = await db.get(User, doctor.user_id)
    if user:
        user.is_verified = True

    await db.commit()
    await db.refresh(doctor)
    return {
        "id": str(doctor.id),
        "user_id": str(doctor.user_id),
        "is_verified": doctor.is_verified,
        "user_is_verified": user.is_verified if user else False,
    }


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
