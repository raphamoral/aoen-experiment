from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ── Course ────────────────────────────────────────────────────────────────────

class CourseCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    instructor: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    duration_hours: int = Field(..., ge=1, le=10_000)


class CourseResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    name: str
    instructor: str
    description: Optional[str]
    duration_hours: int
    active: bool
    created_at: datetime


# ── Certificate ───────────────────────────────────────────────────────────────

class CertificateCreate(BaseModel):
    course_id: str
    recipient_name: str = Field(..., min_length=2, max_length=255)
    recipient_email: EmailStr


class CertificateResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    course_id: str
    recipient_name: str
    # recipient_email deliberadamente ausente: PII não deve sair pela API privada por padrão
    issued_at: datetime
    verification_hash: str
    revoked: bool


# ── Public Verification (sem PII sensível) ────────────────────────────────────

class VerificationResult(BaseModel):
    valid: bool
    course_name: Optional[str] = None
    recipient_name: Optional[str] = None
    issued_at: Optional[datetime] = None
    verification_hash: str
    revoked: bool = False
    message: str = ""