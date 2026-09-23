from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class VerificationResult:
    is_valid: bool
    certificate_id: Optional[str] = None
    student_name: Optional[str] = None
    course_name: Optional[str] = None
    issuer_name: Optional[str] = None
    duration_hours: Optional[int] = None
    issued_at: Optional[datetime] = None
    revocation_reason: Optional[str] = None


class VerifyCertificatePort(ABC):
    @abstractmethod
    def verify_by_hash(self, certificate_hash: str) -> VerificationResult:
        ...

    @abstractmethod
    def verify_by_id(self, certificate_id: str) -> VerificationResult:
        ...