from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Certificate:
    student_id: UUID
    course_id: UUID
    issuer_id: UUID
    id: UUID = field(default_factory=uuid4)
    issued_at: datetime = field(default_factory=datetime.utcnow)
    verification_hash: str = field(default="")
    is_valid: bool = True

    def __post_init__(self) -> None:
        if not self.verification_hash:
            self.verification_hash = self._generate_hash()

    def _generate_hash(self) -> str:
        raw = f"{self.id}{self.student_id}{self.course_id}{self.issued_at.isoformat()}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def revoke(self) -> None:
        if not self.is_valid:
            raise ValueError("Certificate is already revoked")
        self.is_valid = False