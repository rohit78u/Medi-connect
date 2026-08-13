from pathlib import Path

from app.models.medical_document import MedicalDocument


def test_medical_document_columns():
    columns = {column.name for column in MedicalDocument.__table__.columns}
    assert {
        "patient_id", "uploaded_by", "medical_record_id", "lab_report_id",
        "original_filename", "stored_filename", "content_type", "file_size",
        "storage_path", "uploaded_at", "is_active"
    }.issubset(columns)


def test_storage_path_is_not_public_url():
    assert "http://" not in str(Path("storage/medical_documents"))
    assert "https://" not in str(Path("storage/medical_documents"))
