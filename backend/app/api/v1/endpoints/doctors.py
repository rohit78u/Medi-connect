from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_roles
from app.db.session import get_async_db
from app.models.user import User
from app.schemas.doctor import (
    AvailabilitySlotCreate,
    AvailabilitySlotResponse,
    DoctorCreate,
    DoctorResponse
)
from app.schemas.response import APIResponse
from app.services.doctor import DoctorService

router = APIRouter(prefix="/doctors", tags=["Doctors Domain"])


@router.post(
    "/profile",
    response_model=APIResponse[DoctorResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create clinical doctor profile"
)
async def create_doctor_profile(
    data: DoctorCreate,
    current_user: User = Depends(require_roles(["DOCTOR", "ADMIN"])),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Creates a clinical doctor profile for a user with DOCTOR or ADMIN role.
    """
    service = DoctorService(db)
    profile = await service.create_doctor_profile(current_user, data)
    return APIResponse(
        success=True,
        message="Doctor profile created successfully",
        data=profile
    )


@router.get(
    "/search",
    response_model=APIResponse[List[DoctorResponse]],
    status_code=status.HTTP_200_OK,
    summary="Search active doctors by specialization"
)
async def search_doctors(
    specialization: Optional[str] = Query(default=None, description="Specialization filter e.g. Cardiology"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Public search endpoint for patients to find available doctors.
    Only active, user-verified and admin-approved doctor profiles are returned.
    """
    service = DoctorService(db)
    doctors = await service.search_doctors(specialization=specialization, skip=skip, limit=limit)
    return APIResponse(
        success=True,
        message=f"Retrieved {len(doctors)} doctor profiles",
        data=doctors
    )


@router.post(
    "/availability",
    response_model=APIResponse[AvailabilitySlotResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add weekly availability schedule slot"
)
async def add_doctor_availability(
    data: AvailabilitySlotCreate,
    current_user: User = Depends(require_roles(["DOCTOR", "ADMIN"])),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Adds a weekly recurring schedule slot for the authenticated doctor.
    """
    service = DoctorService(db)
    slot = await service.add_availability_slot(current_user, data)
    return APIResponse(
        success=True,
        message="Availability schedule slot added successfully",
        data=slot
    )


@router.get(
    "/availability",
    response_model=APIResponse[List[AvailabilitySlotResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get saved weekly availability schedule"
)
async def get_doctor_availability(
    current_user: User = Depends(require_roles(["DOCTOR", "ADMIN"])),
    db: AsyncSession = Depends(get_async_db)
):
    """Return the saved recurring weekly availability for the authenticated doctor."""
    service = DoctorService(db)
    slots = await service.get_my_availability(current_user)
    return APIResponse(
        success=True,
        message=f"Retrieved {len(slots)} availability slots",
        data=slots
    )
