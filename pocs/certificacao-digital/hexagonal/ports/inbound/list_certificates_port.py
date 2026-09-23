from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class CertificateSummary:
    id: str
    course_name: str
    issuer_name: str
    duration_hours: int
    issued_at: datetime
    is_valid: bool
    certificate_hash: str


@dataclass
class ListCertificatesResult:
    certificates: List[CertificateSummary]
    total: int


class ListCertificatesPort(ABC):
    @abstractmethod
    def list_by_student(self, student_id: str) -> ListCertificatesResult:
        ...

    @abstractmethod
    def get_by_id(self, certificate_id: str) -> Optional[CertificateSummary]:
        ...