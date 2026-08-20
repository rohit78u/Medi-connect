from fastapi import APIRouter
from app.api.v1.endpoints import (
    admin, admin_verification, ai, appointments, auth, doctors, health, medical_records,
    patients, payments, prescriptions, lab_reports, medical_documents,
    websocket,
)

api_v1_router = APIRouter()
api_v1_router.include_router(health.router)
api_v1_router.include_router(auth.router)
api_v1_router.include_router(patients.router)
api_v1_router.include_router(doctors.router)
api_v1_router.include_router(appointments.router)
api_v1_router.include_router(payments.router)
api_v1_router.include_router(ai.router)
api_v1_router.include_router(websocket.router)
api_v1_router.include_router(admin.router)
api_v1_router.include_router(admin_verification.router)
api_v1_router.include_router(medical_records.router)
api_v1_router.include_router(prescriptions.router)
api_v1_router.include_router(lab_reports.router)
api_v1_router.include_router(medical_documents.router)
