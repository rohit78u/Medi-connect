from fastapi import APIRouter, Depends, status
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.ai import (
    MedicalReportParseRequest,
    MedicalReportParseResponse,
    SymptomAnalysisRequest,
    SymptomAnalysisResponse
)
from app.schemas.response import APIResponse
from app.services.ai import AIService

router = APIRouter(prefix="/ai", tags=["AI Clinical Assistant"])


@router.post(
    "/analyze-symptoms",
    response_model=APIResponse[SymptomAnalysisResponse],
    status_code=status.HTTP_200_OK,
    summary="Google Gemini AI Symptom Triage & Clinical Analysis"
)
async def analyze_symptoms(
    req: SymptomAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Analyzes patient symptom descriptions using Google Gemini AI & LangChain to provide preliminary clinical triage.
    """
    service = AIService()
    analysis = await service.analyze_symptoms(req)
    return APIResponse(
        success=True,
        message="Symptom analysis and clinical triage completed",
        data=analysis
    )


@router.post(
    "/parse-medical-report",
    response_model=APIResponse[MedicalReportParseResponse],
    status_code=status.HTTP_200_OK,
    summary="Google Gemini AI Medical Document Parsing"
)
async def parse_medical_report(
    req: MedicalReportParseRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Parses unstructured medical laboratory reports to extract key health metrics and diagnostic insights.
    """
    service = AIService()
    parsed_report = await service.parse_medical_report(req)
    return APIResponse(
        success=True,
        message="Medical report parsed successfully",
        data=parsed_report
    )
