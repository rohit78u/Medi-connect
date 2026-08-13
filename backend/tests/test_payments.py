import hmac
import hashlib
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_payment_order_creation_and_verification(async_client: AsyncClient):
    """
    Test complete payment checkout flow:
    1. Register doctor & patient, create doctor profile, book appointment.
    2. Create Razorpay payment order.
    3. Verify payment signature with valid HMAC digest.
    """
    # 1. Setup Doctor, Patient, and Appointment
    await async_client.post("/api/v1/auth/register", json={
        "email": "pay_doc@mediconnect.ai",
        "password": "DocPassword123!",
        "full_name": "Dr. Pay Doctor",
        "role_name": "DOCTOR"
    })
    doc_login = await async_client.post("/api/v1/auth/login", json={
        "email": "pay_doc@mediconnect.ai",
        "password": "DocPassword123!"
    })
    doc_token = doc_login.json()["data"]["access_token"]

    doc_prof = await async_client.post(
        "/api/v1/doctors/profile",
        json={
            "specialization_name": "Neurology",
            "license_number": "DOC-PAY-112233",
            "consultation_fee": 200.0,
            "years_of_experience": 10
        },
        headers={"Authorization": f"Bearer {doc_token}"}
    )
    doctor_id = doc_prof.json()["data"]["id"]

    await async_client.post("/api/v1/auth/register", json={
        "email": "pay_patient@mediconnect.ai",
        "password": "PatPassword123!",
        "full_name": "Bob Patient",
        "role_name": "PATIENT"
    })
    pat_login = await async_client.post("/api/v1/auth/login", json={
        "email": "pay_patient@mediconnect.ai",
        "password": "PatPassword123!"
    })
    pat_token = pat_login.json()["data"]["access_token"]

    book_res = await async_client.post(
        "/api/v1/appointments/book",
        json={
            "doctor_id": doctor_id,
            "appointment_date": "2026-11-15T14:00:00Z",
            "reason_for_visit": "Neurology Consultation"
        },
        headers={"Authorization": f"Bearer {pat_token}"}
    )
    appointment_id = book_res.json()["data"]["id"]

    # 2. Create Payment Order
    order_res = await async_client.post(
        "/api/v1/payments/create-order",
        json={
            "appointment_id": appointment_id,
            "amount": 200.0,
            "currency": "INR"
        },
        headers={"Authorization": f"Bearer {pat_token}"}
    )
    assert order_res.status_code == 201
    order_data = order_res.json()["data"]
    assert order_data["status"] == "CREATED"
    razorpay_order_id = order_data["razorpay_order_id"]

    # 3. Generate HMAC SHA256 signature for verification test
    razorpay_payment_id = "pay_TEST_99887766"
    secret = "rzp_secret_mediconnect_123"
    msg = f"{razorpay_order_id}|{razorpay_payment_id}".encode("utf-8")
    signature = hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()

    # 4. Verify Payment Signature
    verify_res = await async_client.post(
        "/api/v1/payments/verify",
        json={
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": signature
        },
        headers={"Authorization": f"Bearer {pat_token}"}
    )
    assert verify_res.status_code == 200
    assert verify_res.json()["data"]["status"] == "SUCCESS"
