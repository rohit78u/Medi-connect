import uuid
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_roles
from app.db.session import get_async_db
from app.models.user import User
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentStatusUpdate
)
from app.schemas.response import APIResponse
from app.services.appointment import AppointmentService

router = APIRouter(prefix="/appointments", tags=["Appointment Scheduling"])


@router.post(
    "/book",
    response_model=APIResponse[AppointmentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Book a clinical appointment"
)
async def book_appointment(
    data: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Books an appointment with a doctor, enforcing double-booking prevention guards.
    """
    service = AppointmentService(db)
    appointment = await service.book_appointment(current_user, data)
    return APIResponse(
        success=True,
        message="Appointment booked successfully",
        data=appointment
    )


@router.patch(
    "/{id}/status",
    response_model=APIResponse[AppointmentResponse],
    status_code=status.HTTP_200_OK,
    summary="Update appointment status & clinical notes"
)
async def update_appointment_status(
    id: uuid.UUID,
    data: AppointmentStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    State machine transition for appointment status (PENDING, CONFIRMED, COMPLETED, CANCELLED).
    """
    service = AppointmentService(db)
    updated = await service.update_appointment_status(current_user, id, data)
    return APIResponse(
        success=True,
        message=f"Appointment status updated to {data.status.value}",
        data=updated
    )


@router.get(
    "/my-appointments",
    response_model=APIResponse[List[AppointmentResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get current patient's appointments"
)
async def get_patient_appointments(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Retrieve appointments scheduled for the current patient.
    """
    service = AppointmentService(db)
    appointments = await service.get_patient_appointments(current_user, skip=skip, limit=limit)
    return APIResponse(
        success=True,
        message=f"Retrieved {len(appointments)} patient appointments",
        data=appointments
    )


@router.get(
    "/doctor-schedule",
    response_model=APIResponse[List[AppointmentResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get doctor's clinical schedule"
)
async def get_doctor_schedule(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    current_user: User = Depends(require_roles(["DOCTOR", "ADMIN"])),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Retrieve clinical appointment schedule for the authenticated doctor.
    """
    service = AppointmentService(db)
    appointments = await service.get_doctor_appointments(current_user, skip=skip, limit=limit)
    return APIResponse(
        success=True,
        message=f"Retrieved {len(appointments)} doctor schedule appointments",
        data=appointments
    )
