from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.config import settings
from app.db.session import get_async_db
from app.schemas.response import APIResponse

router = APIRouter(prefix="/health", tags=["Health Checks"])


@router.get(
    "",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="API Health Status Check"
)
async def check_health(db: AsyncSession = Depends(get_async_db)):
    """
    Verifies that the application API service and PostgreSQL database connectivity are operational.
    """
    db_status = "unhealthy"
    try:
        result = await db.execute(text("SELECT 1"))
        if result.scalar() == 1:
            db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    health_data = {
        "status": "online",
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "version": "0.1.0"
    }

    return APIResponse(
        success=True,
        message="MediConnect AI Platform operational",
        data=health_data
    )
