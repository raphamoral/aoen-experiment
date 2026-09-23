from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CertificateIssuedEvent:
    certificate_id: str
    student_id: str
    student_name: str
    student_email: str
    course_id: str
    course_name: str
    issuer_name: str
    issued_at: datetime
    certificate_hash: str
    verification_url: str


@dataclass(frozen=True)
class CertificateRevokedEvent:
    certificate_id: str
    student_id: str
    student_email: str
    revoked_at: datetime
    reason: str