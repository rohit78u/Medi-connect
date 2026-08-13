import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.patient import PatientProfile
from app.repositories.base import BaseRepository


class PatientRepository(BaseRepository[PatientProfile]):
    """
    Repository for Patient Profile data access using Async SQLAlchemy 2.0.
    """
    def __init__(self, db: AsyncSession):
        super().__init__(PatientProfile, db)

    async def get_by_user_id(self, user_id: uuid.UUID) -> Optional[PatientProfile]:
        """
        Fetch patient profile by associated user ID.
        """
        stmt = (
            select(PatientProfile)
            .where(PatientProfile.user_id == user_id, PatientProfile.is_active == True)
            .options(selectinload(PatientProfile.user))
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()
