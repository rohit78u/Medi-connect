from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_async_db
from app.models.user import User
from app.schemas.patient import PatientResponse, PatientUpdate
from app.schemas.response import APIResponse
from app.services.patient import PatientService

router = APIRouter(prefix="/patients", tags=["Patients Domain"])


@router.get(
    "/me",
    response_model=APIResponse[PatientResponse],
    status_code=status.HTTP_200_OK,
    summary="Get current patient profile"
)
async def get_my_patient_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Retrieve or initialize the patient profile for the current user.
    """
    service = PatientService(db)
    profile = await service.get_or_create_patient_profile(current_user)
    return APIResponse(
        success=True,
        message="Patient profile retrieved",
        data=profile
    )


@router.put(
    "/me",
    response_model=APIResponse[PatientResponse],
    status_code=status.HTTP_200_OK,
    summary="Update current patient profile"
)
async def update_my_patient_profile(
    update_data: PatientUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Update patient medical profile fields (DOB, blood group, emergency contact, medical history).
    """
    service = PatientService(db)
    updated = await service.update_patient_profile(current_user, update_data)
    return APIResponse(
        success=True,
        message="Patient profile updated successfully",
        data=updated
    )
