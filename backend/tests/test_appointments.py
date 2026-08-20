import pytest
from httpx import AsyncClient

from app.models.doctor import DoctorProfile


@pytest.mark.asyncio
async def test_appointment_booking_and_double_booking_prevention(
    async_client: AsyncClient,
    db_session,
):
    """Test scheduling against a configured weekly availability slot and conflict prevention."""
    await async_client.post("/api/v1/auth/register", json={
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

    await async_client.post("/api/v1/auth/register", json={
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

    # Simulate the completed admin verification step before booking.
    doctor = await db_session.get(DoctorProfile, doctor_id)
    assert doctor is not None
    doctor.is_verified = True
    await db_session.commit()

    # 2026-10-10 is Saturday (5). Configure a 09:00-17:00 recurring slot.
    availability_res = await async_client.post(
        "/api/v1/doctors/availability",
        json={"day_of_week": 5, "start_time": "09:00", "end_time": "17:00"},
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert availability_res.status_code == 201

    target_slot = "2026-10-10T10:00:00Z"
    book_res = await async_client.post(
        "/api/v1/appointments/book",
        json={"doctor_id": doctor_id, "appointment_date": target_slot, "reason_for_visit": "Annual Heart Checkup"},
        headers={"Authorization": f"Bearer {pat_token}"}
    )
    assert book_res.status_code == 201
    appointment_id = book_res.json()["data"]["id"]
    assert book_res.json()["data"]["status"] == "PENDING"

    conflict_res = await async_client.post(
        "/api/v1/appointments/book",
        json={"doctor_id": doctor_id, "appointment_date": target_slot, "reason_for_visit": "Second booking attempt"},
        headers={"Authorization": f"Bearer {pat_token}"}
    )
    assert conflict_res.status_code == 409

    update_res = await async_client.patch(
        f"/api/v1/appointments/{appointment_id}/status",
        json={"status": "CONFIRMED", "clinical_notes": "Patient confirmed. ECG report requested."},
        headers={"Authorization": f"Bearer {doc_token}"}
    )
    assert update_res.status_code == 200
    assert update_res.json()["data"]["status"] == "CONFIRMED"
