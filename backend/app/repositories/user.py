from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User, Role
from app.models.refresh_token import RefreshToken
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Data Access Repository for User and Role operations using Async SQLAlchemy 2.0.
    """
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = (
            select(User)
            .where(User.email == email.strip().lower())
            .options(selectinload(User.roles))
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_role_by_name(self, name: str) -> Optional[Role]:
        stmt = select(Role).where(Role.name == name.upper().strip())
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create_role_if_not_exists(self, name: str, description: Optional[str] = None) -> Role:
        role_name = name.upper().strip()
        role = await self.get_role_by_name(role_name)
        if not role:
            role = Role(name=role_name, description=description or f"{role_name} Role")
            self.db.add(role)
            await self.db.flush()
            await self.db.refresh(role)
        return role

    async def assign_role_to_user(self, user: User, role: Role) -> None:
        if role not in user.roles:
            user.roles.append(role)
            self.db.add(user)
            await self.db.flush()


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    """Data access for hashed, revocable refresh tokens."""
    def __init__(self, db: AsyncSession):
        super().__init__(RefreshToken, db)

    async def get_active_token(self, token_hash: str) -> Optional[RefreshToken]:
        stmt = (
            select(RefreshToken)
            .where(
                RefreshToken.token == token_hash,
                RefreshToken.is_revoked.is_(False),
                RefreshToken.is_active.is_(True)
            )
            .options(selectinload(RefreshToken.user))
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()
