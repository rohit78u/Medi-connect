import uuid
from datetime import date

from app.models.lab_report import LabReport
from app.schemas.lab_report import LabReportCreate, LabReportResponse


def test_lab_report_model_has_expected_fields():
    columns = set(LabReport.__table__.columns.keys())
    assert {
        "id", "patient_id", "doctor_id", "medical_record_id", "test_name",
        "result", "reference_range", "report_date", "notes", "created_at",
        "updated_at", "is_active", "deleted_at"
    }.issubset(columns)


def test_lab_report_schema_validation():
    patient_id = uuid.uuid4()
    payload = LabReportCreate(
        patient_id=patient_id,
        test_name="Complete Blood Count",
        result="Hemoglobin 13.8 g/dL",
        reference_range="12-16 g/dL",
        report_date=date(2026, 8, 13),
        notes="Routine test",
    )
    assert payload.patient_id == patient_id
    assert payload.test_name == "Complete Blood Count"


def test_lab_report_response_from_attributes():
    patient_id = uuid.uuid4()
    doctor_id = uuid.uuid4()
    report = LabReport(
        patient_id=patient_id,
        doctor_id=doctor_id,
        test_name="Blood glucose",
        result="95 mg/dL",
        report_date=date(2026, 8, 13),
    )
    report.id = uuid.uuid4()
    response = LabReportResponse.model_validate(report, from_attributes=True)
    assert response.patient_id == patient_id
    assert response.doctor_id == doctor_id
