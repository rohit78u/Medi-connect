import hashlib
from datetime import datetime, timedelta, timezone
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


def hash_refresh_token(token: str) -> str:
    """Hash a refresh token before persistence so raw tokens are never stored in the DB."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class AuthService:
    """Authentication workflows, JWT issuance, refresh-token rotation, and RBAC roles."""
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.token_repo = RefreshTokenRepository(db)

    async def register_user(self, req: RegisterRequest) -> UserResponse:
        requested_role = req.role_name.strip().upper()
        if requested_role == "ADMIN":
            raise BadRequestException("ADMIN accounts cannot be created through public registration.")
        if requested_role not in {"PATIENT", "DOCTOR"}:
            raise BadRequestException("Invalid registration role.")

        existing_user = await self.user_repo.get_by_email(req.email)
        if existing_user:
            raise ConflictException(f"User with email '{req.email}' already exists.")

        target_role = await self.user_repo.create_role_if_not_exists(requested_role)
        user_data = {
            "email": req.email.strip().lower(),
            "hashed_password": get_password_hash(req.password),
            "full_name": req.full_name.strip(),
            "phone_number": req.phone_number,
            "is_verified": False,
            "is_superuser": False
        }

        user = await self.user_repo.create(user_data)
        await self.user_repo.assign_role_to_user(user, target_role)
        await self.db.commit()
        updated_user = await self.user_repo.get_by_email(user.email)
        return UserResponse.model_validate(updated_user)

    async def authenticate_user(self, req: LoginRequest) -> TokenResponse:
        user = await self.user_repo.get_by_email(req.email)
        if not user or not verify_password(req.password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password.")
        if not user.is_active:
            raise UnauthorizedException("User account has been deactivated.")

        roles = [r.name for r in user.roles]
        claims = {"roles": roles, "is_superuser": user.is_superuser}
        access_token = create_access_token(subject=user.id, claims=claims)
        refresh_token_str = create_refresh_token(subject=user.id)
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        await self.token_repo.create({
            "user_id": user.id,
            "token": hash_refresh_token(refresh_token_str),
            "expires_at": expires_at
        })
        await self.db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            user=UserResponse.model_validate(user)
        )

    async def refresh_access_token(self, refresh_token_str: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token_str)
            if payload.get("type") != "refresh":
                raise UnauthorizedException("Invalid token type.")
        except Exception:
            raise UnauthorizedException("Invalid or expired refresh token.")

        token_record = await self.token_repo.get_active_token(hash_refresh_token(refresh_token_str))
        if not token_record or token_record.expires_at < datetime.now(timezone.utc):
            raise UnauthorizedException("Refresh token is expired or revoked.")

        user = token_record.user
        if not user or not user.is_active:
            raise UnauthorizedException("User account associated with token is inactive.")

        token_record.is_revoked = True
        roles = [r.name for r in user.roles]
        claims = {"roles": roles, "is_superuser": user.is_superuser}
        new_access_token = create_access_token(subject=user.id, claims=claims)
        new_refresh_token_str = create_refresh_token(subject=user.id)
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        await self.token_repo.create({
            "user_id": user.id,
            "token": hash_refresh_token(new_refresh_token_str),
            "expires_at": expires_at
        })
        await self.db.commit()

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token_str,
            user=UserResponse.model_validate(user)
        )
