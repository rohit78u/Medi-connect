from typing import List, Optional
from pydantic import BaseModel, Field


class SymptomAnalysisRequest(BaseModel):
    symptoms: str = Field(..., min_length=5, example="Persistent dry cough, mild fever 100F, chest tightness for 3 days")
    patient_age: Optional[int] = Field(default=None, ge=0, le=120, example=35)
    gender: Optional[str] = Field(default=None, example="Male")
    medical_history: Optional[str] = Field(default=None, example="Asthma, No allergies")


class SymptomAnalysisResponse(BaseModel):
    triage_level: str = Field(..., example="MODERATE")  # LOW, MODERATE, HIGH, EMERGENCY
    possible_conditions: List[str] = Field(default_factory=list, example=["Acute Bronchitis", "Upper Respiratory Infection"])
    recommended_specialization: str = Field(..., example="Pulmonology")
    clinical_summary: str = Field(..., example="Patient exhibits upper respiratory symptoms with low-grade fever...")
    disclaimer: str = Field(
        default="AI clinical preliminary assessment only. Please consult a licensed medical doctor immediately."
    )


class MedicalReportParseRequest(BaseModel):
    report_text: str = Field(..., min_length=10, example="Complete Blood Count: Hemoglobin 11.2 g/dL, WBC 11,500 /mcL, Platelets 250,000 /mcL.")
    report_type: Optional[str] = Field(default="Lab Report", example="Lab Report")


class MedicalReportParseResponse(BaseModel):
    report_type: str
    key_metrics: List[dict] = Field(default_factory=list, example=[{"metric": "WBC", "value": "11,500 /mcL", "status": "Elevated"}])
    diagnosis_highlights: List[str] = Field(default_factory=list, example=["Mild Leukocytosis indicating possible infection"])
    recommended_actions: List[str] = Field(default_factory=list, example=["Follow up with Primary Care Physician"])
