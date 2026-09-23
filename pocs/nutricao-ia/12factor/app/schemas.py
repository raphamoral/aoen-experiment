"""Schemas Pydantic para validação de entrada/saída."""
import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Any


# ── Users ────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=2, max_length=255)
    age: int | None = Field(None, ge=1, le=120)
    weight_kg: float | None = Field(None, gt=0, le=500)
    height_cm: float | None = Field(None, gt=0, le=300)


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    age: int | None
    weight_kg: float | None
    height_cm: float | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Lab Exams ────────────────────────────────────────────────────────────────

class MarkerValue(BaseModel):
    value: float
    unit: str
    reference_min: float | None = None
    reference_max: float | None = None


class LabExamCreate(BaseModel):
    exam_date: datetime
    lab_name: str | None = None
    markers: dict[str, MarkerValue]


class LabExamOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    exam_date: datetime
    lab_name: str | None
    markers: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Nutrition Recommendations ────────────────────────────────────────────────

class NutritionRecommendationOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    exam_id: uuid.UUID
    ai_model: str
    summary: str
    recommendations: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}