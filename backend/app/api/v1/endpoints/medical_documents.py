import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_async_db
from app.models.medical_document import MedicalDocument
from app.models.patient import PatientProfile
from app.models.user import User
from app.schemas.medical_document import MedicalDocumentResponse

router = APIRouter(prefix="/medical-documents", tags=["medical-documents"])

ALLOWED_TYPES = {"application/pdf", "image/jpeg", "image/png"}
MAX_FILE_SIZE = 10 * 1024 * 1024
STORAGE_ROOT = Path(os.getenv("MEDICAL_DOCUMENT_STORAGE", "storage/medical_documents"))


async def _patient_profile(db: AsyncSession, user_id: uuid.UUID) -> PatientProfile:
    result = await db.execute(select(PatientProfile).where(PatientProfile.user_id == user_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    return profile


@router.post("", response_model=MedicalDocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_medical_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    patient = await _patient_profile(db, current_user.id)
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF, JPEG and PNG files are allowed")

    content = await file.read(MAX_FILE_SIZE + 1)
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Medical document exceeds 10 MB limit")
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    stored_name = f"{uuid.uuid4().hex}{Path(file.filename or 'document').suffix.lower()}"
    STORAGE_ROOT.mkdir(parents=True, exist_ok=True)
    path = STORAGE_ROOT / stored_name
    path.write_bytes(content)

    document = MedicalDocument(
        patient_id=patient.id,
        uploaded_by=current_user.id,
        original_filename=Path(file.filename or "document").name,
        stored_filename=stored_name,
        content_type=file.content_type,
        file_size=len(content),
        storage_path=str(path),
        uploaded_at=datetime.now(timezone.utc),
    )
    db.add(document)
    await db.flush()
    await db.refresh(document)
    return document


@router.get("/me", response_model=List[MedicalDocumentResponse])
async def list_my_documents(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    patient = await _patient_profile(db, current_user.id)
    result = await db.execute(
        select(MedicalDocument)
        .where(MedicalDocument.patient_id == patient.id, MedicalDocument.is_active == True)
        .order_by(MedicalDocument.uploaded_at.desc())
    )
    return list(result.scalars().all())


@router.get("/{document_id}/download")
async def download_medical_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    patient = await _patient_profile(db, current_user.id)
    document = await db.get(MedicalDocument, document_id)
    if not document or document.patient_id != patient.id or not document.is_active:
        raise HTTPException(status_code=404, detail="Medical document not found")
    path = Path(document.storage_path).resolve()
    root = STORAGE_ROOT.resolve()
    if root not in path.parents or not path.is_file():
        raise HTTPException(status_code=404, detail="Stored document not found")
    return FileResponse(path, media_type=document.content_type, filename=document.original_filename)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medical_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    patient = await _patient_profile(db, current_user.id)
    document = await db.get(MedicalDocument, document_id)
    if not document or document.patient_id != patient.id:
        raise HTTPException(status_code=404, detail="Medical document not found")
    document.is_active = False
    return None
