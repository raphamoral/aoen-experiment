from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


# ── Request schemas ──────────────────────────────────────────────────────────

class RegisterPatientRequest(BaseModel):
    name: str
    email: EmailStr
    age: int
    gender: str
    health_goals: list[str] = []

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        if v not in ("M", "F"):
            raise ValueError("gender must be 'M' or 'F'")
        return v

    @field_validator("age")
    @classmethod
    def validate_age(cls, v: int) -> int:
        if not 0 < v < 150:
            raise ValueError("age must be between 1 and 149")
        return v


class ExamResultInput(BaseModel):
    exam_type: str
    value: float
    unit: str
    reference_min: float | None = None
    reference_max: float | None = None


class SubmitLabExamRequest(BaseModel):
    patient_id: UUID
    exam_date: date
    results: list[ExamResultInput]

    @field_validator("results")
    @classmethod
    def validate_results_not_empty(cls, v: list) -> list:
        if not v:
            raise ValueError("results cannot be empty")
        return v


class GenerateNutritionPlanRequest(BaseModel):
    patient_id: UUID
    lab_exam_id: UUID


# ── Response schemas ─────────────────────────────────────────────────────────

class PatientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: str
    age: int
    gender: str
    health_goals: list[str]
    created_at: datetime


class ExamResultResponse(BaseModel):
    exam_type: str
    value: float
    unit: str
    reference_min: float | None
    reference_max: float | None
    is_normal: bool


class LabExamResponse(BaseModel):
    id: UUID
    patient_id: UUID
    exam_date: date
    results: list[ExamResultResponse]
    created_at: datetime


class DietaryRecommendationResponse(BaseModel):
    nutrient: str
    level: str
    foods_to_increase: list[str]
    foods_to_avoid: list[str]
    supplements: list[str]
    clinical_notes: str


class NutritionPlanResponse(BaseModel):
    id: UUID
    patient_id: UUID
    lab_exam_id: UUID
    recommendations: list[DietaryRecommendationResponse]
    general_notes: str
    ai_analysis: str
    has_critical_deficiencies: bool
    abnormal_nutrients: list[str]
    created_at: datetime