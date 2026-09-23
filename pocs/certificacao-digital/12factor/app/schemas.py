from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator


class CertificateCreate(BaseModel):
    recipient_name: str
    recipient_email: EmailStr
    course_name: str
    course_hours: str
    expires_at: Optional[datetime] = None

    @field_validator("recipient_name", "course_name", "course_hours")
    @classmethod
    def must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("field cannot be blank")
        return v.strip()


class CertificateResponse(BaseModel):
    id: UUID
    verification_hash: str
    recipient_name: str
    course_name: str
    course_hours: str
    issuer: str
    issued_at: datetime
    expires_at: Optional[datetime]

    model_config = {"from_attributes": True}


class VerificationResponse(BaseModel):
    valid: bool
    certificate: Optional[CertificateResponse] = None
    message: str