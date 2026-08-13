from uuid import UUID
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.doctor import DoctorProfile
from app.models.user import User

router = APIRouter(prefix="/admin/doctors", tags=["admin-doctors"])


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    roles = getattr(current_user, "roles", []) or []
    if not any(getattr(role, "name", role) == "ADMIN" for role in roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


@router.get("/pending")
async def pending_doctors(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[dict[str, Any]]:
    result = await db.execute(
        select(DoctorProfile).where(DoctorProfile.is_verified.is_(False))
    )
    return [
        {
            "id": str(doctor.id),
            "user_id": str(doctor.user_id),
            "specialization": doctor.specialization,
            "license_number": doctor.license_number,
            "years_of_experience": doctor.years_of_experience,
            "consultation_fee": float(doctor.consultation_fee),
        }
        for doctor in result.scalars().all()
    ]


@router.post("/{doctor_id}/verify")
async def verify_doctor(
    doctor_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict[str, Any]:
    doctor = await db.get(DoctorProfile, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    doctor.is_verified = True
    await db.commit()
    await db.refresh(doctor)
    return {"id": str(doctor.id), "is_verified": doctor.is_verified}


@router.post("/{doctor_id}/reject")
async def reject_doctor(
    doctor_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict[str, Any]:
    doctor = await db.get(DoctorProfile, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    doctor.is_verified = False
    await db.commit()
    return {"id": str(doctor.id), "is_verified": False, "status": "REJECTED"}
