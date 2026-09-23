from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class IssueCertificateCommand:
    student_id: str
    student_name: str
    student_email: str
    course_id: str
    course_name: str
    issuer_name: str
    duration_hours: int


@dataclass
class CertificateIssuedResult:
    certificate_id: str
    certificate_hash: str
    issued_at: datetime
    verification_url: str


class IssueCertificatePort(ABC):
    @abstractmethod
    def issue_certificate(self, command: IssueCertificateCommand) -> CertificateIssuedResult:
        ...