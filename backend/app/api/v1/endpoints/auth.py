from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_roles
from app.db.session import get_async_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshTokenRequest, RegisterRequest, TokenResponse
from app.schemas.response import APIResponse
from app.schemas.user import UserResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication & RBAC"])


@router.post(
    "/register",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new platform user"
)
async def register(
    req: RegisterRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Registers a new user (Patient, Doctor, or Staff) with hashed password and role assignment.
    """
    auth_service = AuthService(db)
    user_response = await auth_service.register_user(req)
    return APIResponse(
        success=True,
        message="User registered successfully",
        data=user_response
    )


@router.post(
    "/login",
    response_model=APIResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and issue JWT Tokens"
)
async def login(
    req: LoginRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Validates user credentials and returns JWT Access and Refresh Tokens.
    """
    auth_service = AuthService(db)
    token_response = await auth_service.authenticate_user(req)
    return APIResponse(
        success=True,
        message="Authentication successful",
        data=token_response
    )


@router.post(
    "/refresh",
    response_model=APIResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Refresh access token"
)
async def refresh_token(
    req: RefreshTokenRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Validates refresh token and returns a new Access Token with rotated Refresh Token.
    """
    auth_service = AuthService(db)
    token_response = await auth_service.refresh_access_token(req.refresh_token)
    return APIResponse(
        success=True,
        message="Token refreshed successfully",
        data=token_response
    )


@router.get(
    "/me",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Get current user profile"
)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Retrieves the currently authenticated user profile and roles.
    """
    return APIResponse(
        success=True,
        message="Current user retrieved",
        data=UserResponse.model_validate(current_user)
    )


@router.get(
    "/doctor-only",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Protected route for Doctors & Admins only"
)
async def doctor_only_route(
    current_user: User = Depends(require_roles(["DOCTOR", "ADMIN"]))
):
    """
    RBAC-protected route accessible only by users with DOCTOR or ADMIN roles.
    """
    return APIResponse(
        success=True,
        message="Access granted to Doctor/Admin clinical dashboard",
        data={"user_id": str(current_user.id), "name": current_user.full_name}
    )
