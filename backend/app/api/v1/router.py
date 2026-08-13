from fastapi import APIRouter
from app.api.v1.endpoints import (
    ai,
    appointments,
    auth,
    doctors,
    health,
    patients,
    payments,
    websocket
)

api_v1_router = APIRouter()

# Register endpoint sub-routers
api_v1_router.include_router(health.router)
api_v1_router.include_router(auth.router)
api_v1_router.include_router(patients.router)
api_v1_router.include_router(doctors.router)
api_v1_router.include_router(appointments.router)
api_v1_router.include_router(payments.router)
api_v1_router.include_router(ai.router)
api_v1_router.include_router(websocket.router)
