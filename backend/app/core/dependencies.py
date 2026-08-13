import uuid
from typing import Callable, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import decode_token
from app.db.session import get_async_db
from app.exceptions.custom_exceptions import ForbiddenException, UnauthorizedException
from app.models.user import User
from app.repositories.user import UserRepository

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
) -> User:
    """
    FastAPI dependency resolving the currently authenticated User from JWT token.
    """
    try:
        payload = decode_token(token)
        user_id_str: str = payload.get("sub")
        token_type: str = payload.get("type")

        if not user_id_str or token_type != "access":
            raise UnauthorizedException("Invalid token credentials")

        user_id = uuid.UUID(user_id_str)
    except Exception as e:
        raise UnauthorizedException(f"Could not validate credentials: {str(e)}")

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)

    if not user:
        raise UnauthorizedException("User not found")
    if not user.is_active:
        raise UnauthorizedException("Inactive user account")

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Ensures current user is active.
    """
    if not current_user.is_active:
        raise UnauthorizedException("User account is disabled")
    return current_user


def require_roles(allowed_roles: List[str]) -> Callable:
    """
    Factory dependency creating Role-Based Access Control (RBAC) authorization guards.
    Usage: Depends(require_roles(["ADMIN", "DOCTOR"]))
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.is_superuser:
            return current_user

        user_role_names = [role.name.upper() for role in current_user.roles]
        allowed_uppercase = [r.upper() for r in allowed_roles]

        has_permission = any(role in allowed_uppercase for role in user_role_names)
        if not has_permission:
            raise ForbiddenException(
                f"Access denied. Requires one of roles: {allowed_roles}"
            )

        return current_user

    return role_checker
