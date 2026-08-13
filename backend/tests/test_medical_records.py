import uuid
from datetime import datetime, timezone

from app.models.medical_record import MedicalRecord
from app.schemas.medical_record import MedicalRecordCreate


def test_medical_record_model_has_expected_columns():
    columns = set(MedicalRecord.__table__.columns.keys())
    assert {
        "id",
        "patient_id",
        "doctor_id",
        "appointment_id",
        "record_date",
        "diagnosis",
        "symptoms",
        "clinical_notes",
        "treatment",
        "created_at",
        "updated_at",
        "is_active",
        "deleted_at",
    }.issubset(columns)


def test_medical_record_create_schema_validates():
    patient_id = uuid.uuid4()
    payload = MedicalRecordCreate(
        patient_id=patient_id,
        record_date=datetime.now(timezone.utc),
        diagnosis="Acute viral infection",
        symptoms="Fever and fatigue",
        clinical_notes="Hydration and rest advised",
        treatment="Supportive care",
    )
    assert payload.patient_id == patient_id
    assert payload.diagnosis == "Acute viral infection"
