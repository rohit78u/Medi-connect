from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import logger
from app.exceptions.custom_exceptions import BaseAppException
from app.schemas.response import APIErrorResponse


def register_exception_handlers(app: FastAPI) -> None:
    """
    Registers custom global exception handlers to guarantee consistent
    API error response schema across all endpoints.
    """

    @app.exception_handler(BaseAppException)
    async def custom_app_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
        logger.warning(f"Domain Exception [{exc.status_code}] on {request.url.path}: {exc.message}")
        error_content = APIErrorResponse(
            success=False,
            message=exc.message,
            errors=exc.errors
        ).model_dump()

        return JSONResponse(
            status_code=exc.status_code,
            content=error_content
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        formatted_errors = []
        for error in exc.errors():
            loc = " -> ".join([str(x) for x in error.get("loc", [])])
            msg = error.get("msg", "Invalid value")
            formatted_errors.append(f"{loc}: {msg}")

        logger.warning(f"Validation Error on {request.url.path}: {formatted_errors}")
        error_content = APIErrorResponse(
            success=False,
            message="Request validation failed",
            errors=formatted_errors
        ).model_dump()

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_content
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        logger.warning(f"HTTP Exception [{exc.status_code}] on {request.url.path}: {exc.detail}")
        error_content = APIErrorResponse(
            success=False,
            message=str(exc.detail),
            errors=[]
        ).model_dump()

        return JSONResponse(
            status_code=exc.status_code,
            content=error_content
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(f"Unhandled Exception on {request.url.path}: {str(exc)}", exc_info=True)
        error_content = APIErrorResponse(
            success=False,
            message="Internal server error",
            errors=[str(exc)] if app.debug else ["An unexpected error occurred."]
        ).model_dump()

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_content
        )
