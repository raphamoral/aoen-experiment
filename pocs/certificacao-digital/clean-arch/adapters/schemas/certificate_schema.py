from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class IssueCertificateRequest(BaseModel):
    student_id: UUID
    course_id: UUID
    issuer_id: UUID


class RevokeCertificateRequest(BaseModel):
    issuer_id: UUID


class CertificateResponse(BaseModel):
    id: UUID
    student_id: UUID
    course_id: UUID
    issuer_id: UUID
    issued_at: datetime
    verification_hash: str
    is_valid: bool

    model_config = {"from_attributes": True}


class VerificationResponse(BaseModel):
    is_valid: bool
    certificate: Optional[CertificateResponse] = None