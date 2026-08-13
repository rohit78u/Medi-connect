from typing import Any, List, Optional
from fastapi import status


class BaseAppException(Exception):
    """
    Root Custom Exception for MediConnect AI application.
    """
    def __init__(
        self,
        message: str = "An unexpected error occurred",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        errors: Optional[List[Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.errors = errors if errors is not None else []
        super().__init__(self.message)


class NotFoundException(BaseAppException):
    def __init__(self, message: str = "Resource not found", errors: Optional[List[Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            errors=errors
        )


class BadRequestException(BaseAppException):
    def __init__(self, message: str = "Bad request", errors: Optional[List[Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=errors
        )


class UnauthorizedException(BaseAppException):
    def __init__(self, message: str = "Unauthorized access", errors: Optional[List[Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            errors=errors
        )


class ForbiddenException(BaseAppException):
    def __init__(self, message: str = "Permission denied", errors: Optional[List[Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            errors=errors
        )


class ConflictException(BaseAppException):
    def __init__(self, message: str = "Resource conflict", errors: Optional[List[Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            errors=errors
        )


class InternalServerErrorException(BaseAppException):
    def __init__(self, message: str = "Internal server error", errors: Optional[List[Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors=errors
        )
