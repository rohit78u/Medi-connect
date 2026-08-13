import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_user_registration(async_client: AsyncClient):
    """
    Test user registration for a Patient role.
    """
    payload = {
        "email": "patient@mediconnect.ai",
        "password": "Password123!",
        "full_name": "John Patient",
        "phone_number": "+123456789",
        "role_name": "PATIENT"
    }

    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == "patient@mediconnect.ai"
    assert data["data"]["full_name"] == "John Patient"
    assert any(role["name"] == "PATIENT" for role in data["data"]["roles"])


@pytest.mark.asyncio
async def test_duplicate_email_registration_fails(async_client: AsyncClient):
    """
    Test registering with an existing email returns 409 Conflict.
    """
    payload = {
        "email": "patient@mediconnect.ai",
        "password": "Password123!",
        "full_name": "John Duplicate",
        "role_name": "PATIENT"
    }

    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    data = response.json()
    assert data["success"] is False
    assert "already exists" in data["message"]


@pytest.mark.asyncio
async def test_user_login(async_client: AsyncClient):
    """
    Test authenticating with valid credentials returns JWT tokens.
    """
    login_payload = {
        "email": "patient@mediconnect.ai",
        "password": "Password123!"
    }

    response = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]
    assert data["data"]["user"]["email"] == "patient@mediconnect.ai"


@pytest.mark.asyncio
async def test_invalid_login_credentials(async_client: AsyncClient):
    """
    Test login with wrong password returns 401 Unauthorized.
    """
    login_payload = {
        "email": "patient@mediconnect.ai",
        "password": "WrongPassword!"
    }

    response = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 401
    assert response.json()["success"] is False


@pytest.mark.asyncio
async def test_rbac_doctor_route_permissions(async_client: AsyncClient):
    """
    Test Role-Based Access Control (RBAC):
    - PATIENT trying to access /doctor-only gets 403 Forbidden.
    - DOCTOR accessing /doctor-only gets 200 OK.
    """
    # 1. Register a Doctor
    doctor_payload = {
        "email": "doctor@mediconnect.ai",
        "password": "DoctorPassword123!",
        "full_name": "Dr. Sarah Smith",
        "role_name": "DOCTOR"
    }
    await async_client.post("/api/v1/auth/register", json=doctor_payload)

    # 2. Login Patient & Doctor to retrieve access tokens
    patient_login = await async_client.post("/api/v1/auth/login", json={
        "email": "patient@mediconnect.ai",
        "password": "Password123!"
    })
    patient_token = patient_login.json()["data"]["access_token"]

    doctor_login = await async_client.post("/api/v1/auth/login", json={
        "email": "doctor@mediconnect.ai",
        "password": "DoctorPassword123!"
    })
    doctor_token = doctor_login.json()["data"]["access_token"]

    # 3. Patient attempts doctor-only route (Expect 403 Forbidden)
    forbidden_resp = await async_client.get(
        "/api/v1/auth/doctor-only",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert forbidden_resp.status_code == 403
    assert forbidden_resp.json()["success"] is False

    # 4. Doctor attempts doctor-only route (Expect 200 OK)
    allowed_resp = await async_client.get(
        "/api/v1/auth/doctor-only",
        headers={"Authorization": f"Bearer {doctor_token}"}
    )
    assert allowed_resp.status_code == 200
    assert allowed_resp.json()["success"] is True
    assert allowed_resp.json()["data"]["name"] == "Dr. Sarah Smith"
