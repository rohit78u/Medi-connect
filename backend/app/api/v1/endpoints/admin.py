from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_roles
from app.db.session import get_async_db
from app.models.appointment import Appointment
from app.models.doctor import DoctorProfile
from app.models.payment import PaymentTransaction
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard", response_model=Dict[str, int])
async def admin_dashboard(
    db: AsyncSession = Depends(get_async_db),
    _: User = Depends(require_roles(["ADMIN"])),
):
    users = await db.scalar(select(func.count(User.id))) or 0
    doctors = await db.scalar(select(func.count(DoctorProfile.id))) or 0
    appointments = await db.scalar(select(func.count(Appointment.id))) or 0
    payments = await db.scalar(select(func.count(PaymentTransaction.id))) or 0
    return {
        "users": users,
        "doctors": doctors,
        "appointments": appointments,
        "payments": payments,
    }


@router.get("/users")
async def admin_users(
    db: AsyncSession = Depends(get_async_db),
    _: User = Depends(require_roles(["ADMIN"])),
) -> List[Dict[str, Any]]:
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return [
        {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "phone_number": user.phone_number,
            "is_verified": user.is_verified,
            "is_active": user.is_active,
            "roles": [role.name for role in user.roles],
        }
        for user in result.scalars().all()
    ]


@router.get("/appointments")
async def admin_appointments(
    db: AsyncSession = Depends(get_async_db),
    _: User = Depends(require_roles(["ADMIN"])),
) -> List[Dict[str, Any]]:
    result = await db.execute(
        select(Appointment).order_by(Appointment.appointment_date.desc())
    )
    return [
        {
            "id": str(item.id),
            "patient_id": str(item.patient_id),
            "doctor_id": str(item.doctor_id),
            "appointment_date": item.appointment_date.isoformat(),
            "status": item.status.value,
            "reason_for_visit": item.reason_for_visit,
        }
        for item in result.scalars().all()
    ]


@router.get("/payments")
async def admin_payments(
    db: AsyncSession = Depends(get_async_db),
    _: User = Depends(require_roles(["ADMIN"])),
) -> List[Dict[str, Any]]:
    result = await db.execute(
        select(PaymentTransaction).order_by(PaymentTransaction.created_at.desc())
    )
    return [
        {
            "id": str(item.id),
            "appointment_id": str(item.appointment_id),
            "user_id": str(item.user_id),
            "order_id": item.razorpay_order_id,
            "amount": float(item.amount),
            "currency": item.currency,
            "status": item.status.value,
        }
        for item in result.scalars().all()
    ]
