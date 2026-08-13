import uuid
from datetime import date

from app.models.prescription import Prescription
from app.schemas.prescription import PrescriptionCreate


def test_prescription_model_has_expected_columns():
    columns = set(Prescription.__table__.columns.keys())
    assert {
        "id",
        "patient_id",
        "doctor_id",
        "medical_record_id",
        "medicine_name",
        "dosage",
        "frequency",
        "duration",
        "instructions",
        "prescribed_date",
        "created_at",
        "updated_at",
        "is_active",
        "deleted_at",
    }.issubset(columns)


def test_prescription_create_schema_validates():
    patient_id = uuid.uuid4()
    payload = PrescriptionCreate(
        patient_id=patient_id,
        medicine_name="Amoxicillin",
        dosage="500 mg",
        frequency="Twice daily",
        duration="5 days",
        instructions="Take after food",
        prescribed_date=date.today(),
    )
    assert payload.patient_id == patient_id
    assert payload.medicine_name == "Amoxicillin"
    assert payload.duration == "5 days"
