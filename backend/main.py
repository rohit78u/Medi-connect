from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.logging import logger, setup_logging
from app.middleware.exception_handler import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan hooks.

    Database schema changes are managed explicitly through Alembic migrations;
    the application no longer creates tables automatically at startup.
    """
    setup_logging()
    logger.info(f"Starting {settings.PROJECT_NAME} API in [{settings.ENVIRONMENT}] mode...")
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME} API gracefully...")


def create_application() -> FastAPI:
    """
    Application Factory pattern creating and configuring the FastAPI instance.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="Production-grade Healthcare SaaS Platform backend powered by FastAPI, SQLAlchemy 2.0, & Google Gemini AI.",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(api_v1_router, prefix=settings.API_V1_STR)

    return app


app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
