import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User, Role, UserRole
from app.models.refresh_token import RefreshToken
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Data Access Repository for User and Role operations using Async SQLAlchemy 2.0.
    """
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Fetch user by email address with eager loaded roles.
        """
        stmt = (
            select(User)
            .where(User.email == email.strip().lower())
            .options(selectinload(User.roles))
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_role_by_name(self, name: str) -> Optional[Role]:
        """
        Fetch role model by role name.
        """
        stmt = select(Role).where(Role.name == name.upper().strip())
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create_role_if_not_exists(self, name: str, description: Optional[str] = None) -> Role:
        """
        Ensure role exists in the database.
        """
        role_name = name.upper().strip()
        role = await self.get_role_by_name(role_name)
        if not role:
            role = Role(name=role_name, description=description or f"{role_name} Role")
            self.db.add(role)
            await self.db.flush()
            await self.db.refresh(role)
        return role

    async def assign_role_to_user(self, user: User, role: Role) -> None:
        """
        Assign a role to a user.
        """
        if role not in user.roles:
            user.roles.append(role)
            self.db.add(user)
            await self.db.flush()


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    """
    Data Access Repository for Refresh Token management.
    """
    def __init__(self, db: AsyncSession):
        super().__init__(RefreshToken, db)

    async def get_active_token(self, token_str: str) -> Optional[RefreshToken]:
        """
        Fetch active unrevoked refresh token.
        """
        stmt = (
            select(RefreshToken)
            .where(
                RefreshToken.token == token_str,
                RefreshToken.is_revoked == False,
                RefreshToken.is_active == True
            )
            .options(selectinload(RefreshToken.user))
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()
