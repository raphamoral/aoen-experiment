from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class IssueCertificateRequest(BaseModel):
    student_id: str = Field(..., description="Unique student identifier")
    student_name: str = Field(..., min_length=2)
    student_email: EmailStr
    course_id: str = Field(..., description="Unique course identifier")
    course_name: str = Field(..., min_length=2)
    issuer_name: str = Field(..., description="Institution issuing the certificate")
    duration_hours: int = Field(..., gt=0, description="Course workload in hours")


class IssueCertificateResponse(BaseModel):
    certificate_id: str
    certificate_hash: str
    issued_at: datetime
    verification_url: str


class VerificationResponse(BaseModel):
    is_valid: bool
    certificate_id: Optional[str] = None
    student_name: Optional[str] = None
    course_name: Optional[str] = None
    issuer_name: Optional[str] = None
    duration_hours: Optional[int] = None
    issued_at: Optional[datetime] = None
    revocation_reason: Optional[str] = None


class RevokeCertificateRequest(BaseModel):
    reason: str = Field(..., min_length=5, description="Mandatory revocation justification")


class CertificateSummaryResponse(BaseModel):
    id: str
    course_name: str
    issuer_name: str
    duration_hours: int
    issued_at: datetime
    is_valid: bool
    certificate_hash: str


class ListCertificatesResponse(BaseModel):
    certificates: List[CertificateSummaryResponse]
    total: int