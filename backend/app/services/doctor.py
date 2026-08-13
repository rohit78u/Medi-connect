import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.custom_exceptions import BadRequestException, NotFoundException
from app.models.user import User
from app.repositories.doctor import DoctorRepository, SpecializationRepository
from app.schemas.doctor import (
    AvailabilitySlotCreate,
    AvailabilitySlotResponse,
    DoctorCreate,
    DoctorResponse
)


class DoctorService:
    """
    Business Logic Service for Doctor profile, specializations, and schedule slots.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        self.doctor_repo = DoctorRepository(db)
        self.spec_repo = SpecializationRepository(db)

    async def create_doctor_profile(
        self,
        user: User,
        data: DoctorCreate
    ) -> DoctorResponse:
        """
        Create doctor clinical profile.
        """
        existing = await self.doctor_repo.get_by_user_id(user.id)
        if existing:
            raise BadRequestException("Doctor profile already exists for this user.")

        # Specialization resolution
        spec = await self.spec_repo.get_by_name(data.specialization_name)
        if not spec:
            spec = await self.spec_repo.create({
                "name": data.specialization_name.strip(),
                "description": f"{data.specialization_name.strip()} department"
            })

        profile_data = {
            "user_id": user.id,
            "specialization_id": spec.id,
            "license_number": data.license_number.strip(),
            "consultation_fee": data.consultation_fee,
            "years_of_experience": data.years_of_experience,
            "bio": data.bio
        }

        profile = await self.doctor_repo.create(profile_data)
        await self.db.commit()

        refetched = await self.doctor_repo.get_by_user_id(user.id)
        return DoctorResponse.model_validate(refetched)

    async def search_doctors(
        self,
        specialization: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[DoctorResponse]:
        """
        Search doctors by specialization name.
        """
        doctors = await self.doctor_repo.search_doctors(
            specialization_name=specialization,
            skip=skip,
            limit=limit
        )
        return [DoctorResponse.model_validate(doc) for doc in doctors]

    async def add_availability_slot(
        self,
        user: User,
        data: AvailabilitySlotCreate
    ) -> AvailabilitySlotResponse:
        """
        Add a weekly schedule slot for the doctor.
        """
        doctor = await self.doctor_repo.get_by_user_id(user.id)
        if not doctor:
            raise NotFoundException("Doctor profile not found for user.")

        slot = await self.doctor_repo.add_availability(
            doctor_id=doctor.id,
            day_of_week=data.day_of_week,
            start_time=data.start_time,
            end_time=data.end_time
        )
        await self.db.commit()
        return AvailabilitySlotResponse.model_validate(slot)
