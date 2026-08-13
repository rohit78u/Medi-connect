import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.doctor import DoctorAvailability, DoctorProfile, Specialization
from app.repositories.base import BaseRepository


class SpecializationRepository(BaseRepository[Specialization]):
    def __init__(self, db: AsyncSession):
        super().__init__(Specialization, db)

    async def get_by_name(self, name: str) -> Optional[Specialization]:
        stmt = select(Specialization).where(Specialization.name.ilike(name.strip()))
        result = await self.db.execute(stmt)
        return result.scalars().first()


class DoctorRepository(BaseRepository[DoctorProfile]):
    """Repository for Doctor Profile and Availability data access."""
    def __init__(self, db: AsyncSession):
        super().__init__(DoctorProfile, db)

    async def get_by_user_id(self, user_id: uuid.UUID) -> Optional[DoctorProfile]:
        stmt = (
            select(DoctorProfile)
            .where(DoctorProfile.user_id == user_id, DoctorProfile.is_active == True)
            .options(
                selectinload(DoctorProfile.user),
                selectinload(DoctorProfile.specialization),
                selectinload(DoctorProfile.availabilities)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def search_doctors(
        self,
        specialization_name: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[DoctorProfile]:
        """Return only active and verified doctors that patients can book."""
        stmt = (
            select(DoctorProfile)
            .join(DoctorProfile.user)
            .where(
                DoctorProfile.is_active == True,
                User.is_verified == True,
            )
        )
        if specialization_name:
            stmt = stmt.join(DoctorProfile.specialization).where(
                Specialization.name.ilike(f"%{specialization_name.strip()}%")
            )

        stmt = (
            stmt.options(
                selectinload(DoctorProfile.user),
                selectinload(DoctorProfile.specialization),
                selectinload(DoctorProfile.availabilities)
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def add_availability(
        self,
        doctor_id: uuid.UUID,
        day_of_week: int,
        start_time: str,
        end_time: str
    ) -> DoctorAvailability:
        slot = DoctorAvailability(
            doctor_id=doctor_id,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time
        )
        self.db.add(slot)
        await self.db.flush()
        await self.db.refresh(slot)
        return slot
