import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.custom_exceptions import NotFoundException
from app.models.user import User
from app.repositories.patient import PatientRepository
from app.schemas.patient import PatientCreate, PatientResponse, PatientUpdate


class PatientService:
    """
    Business Logic Service for Patient profile creation and updates.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        self.patient_repo = PatientRepository(db)

    async def get_or_create_patient_profile(self, user: User) -> PatientResponse:
        """
        Get or initialize patient profile for user.
        """
        profile = await self.patient_repo.get_by_user_id(user.id)
        if not profile:
            profile = await self.patient_repo.create({"user_id": user.id})
            await self.db.commit()
            profile = await self.patient_repo.get_by_user_id(user.id)

        return PatientResponse.model_validate(profile)

    async def update_patient_profile(
        self,
        user: User,
        update_data: PatientUpdate
    ) -> PatientResponse:
        """
        Update patient profile attributes.
        """
        profile = await self.patient_repo.get_by_user_id(user.id)
        if not profile:
            profile = await self.patient_repo.create({"user_id": user.id})

        fields = update_data.model_dump(exclude_unset=True)
        updated_profile = await self.patient_repo.update(profile, fields)
        await self.db.commit()

        refetched = await self.patient_repo.get_by_user_id(user.id)
        return PatientResponse.model_validate(refetched)
