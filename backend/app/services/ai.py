from app.ai.gemini_service import gemini_ai_service
from app.schemas.ai import (
    MedicalReportParseRequest,
    MedicalReportParseResponse,
    SymptomAnalysisRequest,
    SymptomAnalysisResponse
)


class AIService:
    """
    Domain Service for AI clinical assistant interactions.
    """
    def __init__(self):
        self.ai_engine = gemini_ai_service

    async def analyze_symptoms(self, req: SymptomAnalysisRequest) -> SymptomAnalysisResponse:
        return await self.ai_engine.analyze_symptoms(req)

    async def parse_medical_report(self, req: MedicalReportParseRequest) -> MedicalReportParseResponse:
        return await self.ai_engine.parse_medical_report(req)
