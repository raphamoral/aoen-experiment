from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from domain.exceptions import CertificateAlreadyRevokedError


@dataclass
class Certificate:
    """
    Aggregate root for the Certificate bounded context.

    A Certificate is issued when a Student completes a Course.
    Its hash enables tamper-evident public verification: anyone holding
    the hash can confirm the certificate's authenticity without trusting
    any central authority beyond the hash itself.
    """

    student_id: str
    course_id: str
    student_name: str
    course_name: str
    issuer_name: str
    duration_hours: int
    issued_at: datetime
    certificate_hash: str
    id: str = field(default="")
    is_valid: bool = True
    revoked_at: Optional[datetime] = None
    revocation_reason: Optional[str] = None

    def revoke(self, reason: str) -> None:
        if not self.is_valid:
            raise CertificateAlreadyRevokedError(self.id)
        self.is_valid = False
        self.revoked_at = datetime.utcnow()
        self.revocation_reason = reason

    def is_authentic(self, provided_hash: str) -> bool:
        return self.certificate_hash == provided_hash and self.is_valid