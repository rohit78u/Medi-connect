import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_appointment_booking_and_double_booking_prevention(async_client: AsyncClient):
    """
    Test complete appointment workflow:
    1. Register Doctor & Patient.
    2. Create Doctor Clinical Profile.
    3. Patient books appointment slot.
    4. Second appointment booking for same doctor slot returns 409 Conflict.
    5. Doctor updates status to CONFIRMED with clinical notes.
    """
    # 1. Register Doctor & Patient
    doc_reg = await async_client.post("/api/v1/auth/register", json={
        "email": "cardio_doc@mediconnect.ai",
        "password": "DocPassword123!",
        "full_name": "Dr. Alex Vance",
        "role_name": "DOCTOR"
    })
    doc_token_res = await async_client.post("/api/v1/auth/login", json={
        "email": "cardio_doc@mediconnect.ai",
        "password": "DocPassword123!"
    })
    doc_token = doc_token_res.json()["data"]["access_token"]

    pat_reg = await async_client.post("/api/v1/auth/register", json={
        "email": "cardio_patient@mediconnect.ai",
        "password": "PatPassword123!",
        "full_name": "Alice Patient",
        "role_name": "PATIENT"
    })
    pat_token_res = await async_client.post("/api/v1/auth/login", json={
        "email": "cardio_patient@mediconnect.ai",
        "password": "PatPassword123!"
    })
    pat_token = pat_token_res.json()["data"]["access_token"]

    # 2. Create Doctor Clinical Profile
    doc_prof_res = await async_client.post(
        "/api/v1/doctors/profile",
        json={
            "specialization_name": "Cardiology",
            "license_number": "DOC-998877",
            "consultation_fee": 150.0,
            "years_of_experience": 12,
            "bio": "Expert Cardiologist"
        },
        headers={"Authorization": f"Bearer {doc_token}"}
    )
    assert doc_prof_res.status_code == 201
    doctor_id = doc_prof_res.json()["data"]["id"]

    # 3. Patient books appointment slot
    target_slot = "2026-10-10T10:00:00Z"
    book_res = await async_client.post(
        "/api/v1/appointments/book",
        json={
            "doctor_id": doctor_id,
            "appointment_date": target_slot,
            "reason_for_visit": "Annual Heart Checkup"
        },
        headers={"Authorization": f"Bearer {pat_token}"}
    )
    assert book_res.status_code == 201
    book_data = book_res.json()["data"]
    assert book_data["status"] == "PENDING"
    appointment_id = book_data["id"]

    # 4. Double-booking attempt for same slot -> Expect 409 Conflict
    conflict_res = await async_client.post(
        "/api/v1/appointments/book",
        json={
            "doctor_id": doctor_id,
            "appointment_date": target_slot,
            "reason_for_visit": "Second booking attempt"
        },
        headers={"Authorization": f"Bearer {pat_token}"}
    )
    assert conflict_res.status_code == 409
    assert conflict_res.json()["success"] is False

    # 5. Doctor updates status to CONFIRMED with clinical notes
    update_res = await async_client.patch(
        f"/api/v1/appointments/{appointment_id}/status",
        json={
            "status": "CONFIRMED",
            "clinical_notes": "Patient confirmed. ECG report requested."
        },
        headers={"Authorization": f"Bearer {doc_token}"}
    )
    assert update_res.status_code == 200
    assert update_res.json()["data"]["status"] == "CONFIRMED"
    assert update_res.json()["data"]["clinical_notes"] == "Patient confirmed. ECG report requested."
