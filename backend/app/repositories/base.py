import uuid
from typing import Any, Generic, List, Optional, Type, TypeVar
from datetime import datetime, timezone
from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Abstract Generic Repository implementing Async SQLAlchemy 2.0 Data Access Patterns.
    """
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(
        self,
        id: uuid.UUID,
        include_inactive: bool = False
    ) -> Optional[ModelType]:
        """
        Fetch a single record by primary key UUID.
        """
        query = select(self.model).where(self.model.id == id)
        if not include_inactive and hasattr(self.model, "is_active"):
            query = query.where(self.model.is_active == True)

        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        include_inactive: bool = False
    ) -> List[ModelType]:
        """
        Fetch all records with optional pagination.
        """
        query = select(self.model)
        if not include_inactive and hasattr(self.model, "is_active"):
            query = query.where(self.model.is_active == True)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count(self, include_inactive: bool = False) -> int:
        """
        Count total records.
        """
        query = select(func.count()).select_from(self.model)
        if not include_inactive and hasattr(self.model, "is_active"):
            query = query.where(self.model.is_active == True)

        result = await self.db.execute(query)
        return result.scalar() or 0

    async def create(self, obj_in_data: dict[str, Any]) -> ModelType:
        """
        Create and persist a new model instance.
        """
        db_obj = self.model(**obj_in_data)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db_obj: ModelType,
        obj_in_data: dict[str, Any]
    ) -> ModelType:
        """
        Update an existing model instance.
        """
        for field, value in obj_in_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        if hasattr(db_obj, "updated_at"):
            setattr(db_obj, "updated_at", datetime.now(timezone.utc))

        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def soft_delete(self, id: uuid.UUID) -> bool:
        """
        Soft delete a record by setting `is_active=False` and timestamping `deleted_at`.
        """
        db_obj = await self.get_by_id(id)
        if not db_obj:
            return False

        if hasattr(db_obj, "is_active"):
            setattr(db_obj, "is_active", False)
        if hasattr(db_obj, "deleted_at"):
            setattr(db_obj, "deleted_at", datetime.now(timezone.utc))

        self.db.add(db_obj)
        await self.db.flush()
        return True

    async def hard_delete(self, id: uuid.UUID) -> bool:
        """
        Permanently delete a record from the database.
        """
        stmt = delete(self.model).where(self.model.id == id)
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.rowcount > 0
