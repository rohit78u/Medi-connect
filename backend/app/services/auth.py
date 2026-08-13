from datetime import datetime, timedelta, timezone
from typing import Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password
)
from app.exceptions.custom_exceptions import (
    BadRequestException,
    ConflictException,
    UnauthorizedException
)
from app.models.user import User
from app.repositories.user import RefreshTokenRepository, UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserResponse


class AuthService:
    """
    Business Logic Service orchestrating authentication workflows, JWT tokens, and RBAC roles.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.token_repo = RefreshTokenRepository(db)

    async def register_user(self, req: RegisterRequest) -> UserResponse:
        """
        Register a new user, hash password, assign requested role, and persist to database.
        """
        existing_user = await self.user_repo.get_by_email(req.email)
        if existing_user:
            raise ConflictException(f"User with email '{req.email}' already exists.")

        # Ensure requested role exists
        target_role = await self.user_repo.create_role_if_not_exists(req.role_name)

        hashed_pwd = get_password_hash(req.password)
        user_data = {
            "email": req.email.strip().lower(),
            "hashed_password": hashed_pwd,
            "full_name": req.full_name.strip(),
            "phone_number": req.phone_number,
            "is_verified": False,
            "is_superuser": False
        }

        user = await self.user_repo.create(user_data)
        await self.user_repo.assign_role_to_user(user, target_role)
        await self.db.commit()

        # Re-fetch user with loaded roles
        updated_user = await self.user_repo.get_by_email(user.email)
        return UserResponse.model_validate(updated_user)

    async def authenticate_user(self, req: LoginRequest) -> TokenResponse:
        """
        Authenticate user credentials and issue Access and Refresh JWT Tokens.
        """
        user = await self.user_repo.get_by_email(req.email)
        if not user or not verify_password(req.password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password.")

        if not user.is_active:
            raise UnauthorizedException("User account has been deactivated.")

        # Extract role names for JWT claims
        roles = [r.name for r in user.roles]
        claims = {"roles": roles, "is_superuser": user.is_superuser}

        access_token = create_access_token(subject=user.id, claims=claims)
        refresh_token_str = create_refresh_token(subject=user.id)

        # Store Refresh Token in DB
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await self.token_repo.create({
            "user_id": user.id,
            "token": refresh_token_str,
            "expires_at": expires_at
        })
        await self.db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            user=UserResponse.model_validate(user)
        )

    async def refresh_access_token(self, refresh_token_str: str) -> TokenResponse:
        """
        Validate refresh token, rotate tokens, and issue a new access token.
        """
        try:
            payload = decode_token(refresh_token_str)
            if payload.get("type") != "refresh":
                raise UnauthorizedException("Invalid token type.")
        except Exception as e:
            raise UnauthorizedException(f"Invalid or expired refresh token: {str(e)}")

        token_record = await self.token_repo.get_active_token(refresh_token_str)
        if not token_record or token_record.expires_at < datetime.now(timezone.utc):
            raise UnauthorizedException("Refresh token is expired or revoked.")

        user = token_record.user
        if not user or not user.is_active:
            raise UnauthorizedException("User account associated with token is inactive.")

        # Revoke old refresh token (rotation policy)
        await self.token_repo.update(token_record, {"is_revoked": True})

        # Issue new tokens
        roles = [r.name for r in user.roles]
        claims = {"roles": roles, "is_superuser": user.is_superuser}

        new_access_token = create_access_token(subject=user.id, claims=claims)
        new_refresh_token_str = create_refresh_token(subject=user.id)

        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await self.token_repo.create({
            "user_id": user.id,
            "token": new_refresh_token_str,
            "expires_at": expires_at
        })
        await self.db.commit()

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token_str,
            user=UserResponse.model_validate(user)
        )
