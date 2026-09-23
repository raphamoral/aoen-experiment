from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


class ProposalStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"


@dataclass
class Proposal:
    project_id: str
    freelancer_id: str
    price: float
    cover_letter: str
    estimated_days: int
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: ProposalStatus = ProposalStatus.PENDING
    submitted_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def __post_init__(self):
        self._validate()

    def _validate(self):
        if self.price <= 0:
            raise ValueError("Price must be positive")
        if self.estimated_days <= 0:
            raise ValueError("Estimated days must be positive")
        if not self.cover_letter or len(self.cover_letter.strip()) < 10:
            raise ValueError("Cover letter must have at least 10 characters")

    def accept(self) -> None:
        if self.status != ProposalStatus.PENDING:
            raise ValueError(f"Cannot accept proposal with status '{self.status}'")
        self.status = ProposalStatus.ACCEPTED

    def reject(self) -> None:
        if self.status != ProposalStatus.PENDING:
            raise ValueError(f"Cannot reject proposal with status '{self.status}'")
        self.status = ProposalStatus.REJECTED

    def withdraw(self) -> None:
        if self.status != ProposalStatus.PENDING:
            raise ValueError(f"Cannot withdraw proposal with status '{self.status}'")
        self.status = ProposalStatus.WITHDRAWN