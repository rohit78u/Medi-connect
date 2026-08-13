import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_ai_symptom_analysis_and_report_parsing(async_client: AsyncClient):
    """
    Test Google Gemini AI symptom triage and medical report parsing endpoints.
    """
    # 1. Register & Login Patient
    await async_client.post("/api/v1/auth/register", json={
        "email": "ai_patient@mediconnect.ai",
        "password": "PatPassword123!",
        "full_name": "Carol Patient",
        "role_name": "PATIENT"
    })
    pat_login = await async_client.post("/api/v1/auth/login", json={
        "email": "ai_patient@mediconnect.ai",
        "password": "PatPassword123!"
    })
    pat_token = pat_login.json()["data"]["access_token"]

    # 2. Test Symptom Analysis
    symptom_res = await async_client.post(
        "/api/v1/ai/analyze-symptoms",
        json={
            "symptoms": "Persistent chest pain and shortness of breath for 2 hours",
            "patient_age": 55,
            "gender": "Male"
        },
        headers={"Authorization": f"Bearer {pat_token}"}
    )
    assert symptom_res.status_code == 200
    sym_data = symptom_res.json()["data"]
    assert sym_data["triage_level"] == "EMERGENCY"
    assert "Cardiology" in sym_data["recommended_specialization"]

    # 3. Test Medical Report Parsing
    report_res = await async_client.post(
        "/api/v1/ai/parse-medical-report",
        json={
            "report_text": "Complete Blood Count: WBC 12,000 /mcL, Hemoglobin 14.0 g/dL, Platelets 220,000 /mcL.",
            "report_type": "CBC Lab Report"
        },
        headers={"Authorization": f"Bearer {pat_token}"}
    )
    assert report_res.status_code == 200
    report_data = report_res.json()["data"]
    assert report_data["report_type"] == "CBC Lab Report"
    assert len(report_data["key_metrics"]) > 0
