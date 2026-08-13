import json
from typing import Any

import httpx

from app.core.config import settings
from app.core.logging import logger
from app.schemas.ai import (
    MedicalReportParseRequest,
    MedicalReportParseResponse,
    SymptomAnalysisRequest,
    SymptomAnalysisResponse,
)


class GeminiAIService:
    """Gemini-backed clinical assistance with validated JSON and a safe local fallback."""

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
    DISCLAIMER = (
        "AI preliminary clinical support only. This is not a diagnosis or a substitute "
        "for a licensed medical professional. Seek urgent care for severe or worsening symptoms."
    )

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL

    async def _generate_json(self, prompt: str, response_schema: dict) -> dict[str, Any] | None:
        if not self.api_key:
            return None

        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "response_mime_type": "application/json",
                "response_schema": response_schema,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.BASE_URL}/models/{self.model}:generateContent",
                    headers={"x-goog-api-key": self.api_key, "Content-Type": "application/json"},
                    json=payload,
                )
            response.raise_for_status()
            body = response.json()
            text = body["candidates"][0]["content"]["parts"][0]["text"]
            parsed = json.loads(text)
            if not isinstance(parsed, dict):
                raise ValueError("Gemini returned a non-object JSON response")
            return parsed
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
            logger.exception("Gemini request/validation failed: %s", exc)
            return None

    async def analyze_symptoms(self, req: SymptomAnalysisRequest) -> SymptomAnalysisResponse:
        prompt = f"""
You are a clinical decision-support assistant. Do not diagnose. Assess urgency and suggest an
appropriate medical specialty for clinician follow-up. Never invent measurements or history.
Use only the information supplied by the user. If symptoms could indicate an emergency, set
triage_level to EMERGENCY and clearly recommend immediate emergency evaluation.

Patient age: {req.patient_age}
Gender: {req.gender}
Medical history: {req.medical_history}
Symptoms: {req.symptoms}
""".strip()

        schema = {
            "type": "OBJECT",
            "properties": {
                "triage_level": {"type": "STRING", "enum": ["LOW", "MODERATE", "HIGH", "EMERGENCY"]},
                "possible_conditions": {"type": "ARRAY", "items": {"type": "STRING"}},
                "recommended_specialization": {"type": "STRING"},
                "clinical_summary": {"type": "STRING"},
            },
            "required": ["triage_level", "possible_conditions", "recommended_specialization", "clinical_summary"],
        }
        result = await self._generate_json(prompt, schema)
        if result is None:
            result = self._symptom_fallback(req)

        return SymptomAnalysisResponse(
            triage_level=result.get("triage_level", "LOW"),
            possible_conditions=result.get("possible_conditions", [])[:5],
            recommended_specialization=result.get("recommended_specialization", "General Practice"),
            clinical_summary=result.get("clinical_summary", "Clinical review is recommended."),
            disclaimer=self.DISCLAIMER,
        )

    async def parse_medical_report(self, req: MedicalReportParseRequest) -> MedicalReportParseResponse:
        prompt = f"""
You are a medical-report extraction assistant. Extract only information explicitly present in the
report. Do not invent laboratory values or diagnose the patient. Return concise structured data.
Report type: {req.report_type}
Report text:
{req.report_text}
""".strip()

        schema = {
            "type": "OBJECT",
            "properties": {
                "report_type": {"type": "STRING"},
                "key_metrics": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "metric": {"type": "STRING"},
                            "value": {"type": "STRING"},
                            "status": {"type": "STRING"},
                        },
                        "required": ["metric", "value", "status"],
                    },
                },
                "diagnosis_highlights": {"type": "ARRAY", "items": {"type": "STRING"}},
                "recommended_actions": {"type": "ARRAY", "items": {"type": "STRING"}},
            },
            "required": ["report_type", "key_metrics", "diagnosis_highlights", "recommended_actions"],
        }
        result = await self._generate_json(prompt, schema)
        if result is None:
            result = self._report_fallback(req)

        return MedicalReportParseResponse(
            report_type=str(result.get("report_type") or req.report_type or "Laboratory Report"),
            key_metrics=result.get("key_metrics", [])[:20],
            diagnosis_highlights=result.get("diagnosis_highlights", [])[:10],
            recommended_actions=result.get("recommended_actions", [])[:10],
        )

    @staticmethod
    def _symptom_fallback(req: SymptomAnalysisRequest) -> dict[str, Any]:
        symptoms = req.symptoms.lower()
        emergency_terms = ["chest pain", "severe breathing", "shortness of breath", "unconscious", "severe bleeding"]
        if any(term in symptoms for term in emergency_terms):
            return {
                "triage_level": "EMERGENCY",
                "possible_conditions": [],
                "recommended_specialization": "Emergency Medicine",
                "clinical_summary": "Potentially serious symptoms detected; seek immediate medical evaluation.",
            }
        return {
            "triage_level": "LOW",
            "possible_conditions": [],
            "recommended_specialization": "General Practice",
            "clinical_summary": "No emergency pattern was detected by the offline fallback; routine clinical review is recommended.",
        }

    @staticmethod
    def _report_fallback(req: MedicalReportParseRequest) -> dict[str, Any]:
        return {
            "report_type": req.report_type or "Laboratory Report",
            "key_metrics": [],
            "diagnosis_highlights": [],
            "recommended_actions": ["Share the report with a licensed medical professional."],
        }


gemini_ai_service = GeminiAIService()
