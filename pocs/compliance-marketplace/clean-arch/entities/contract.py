from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class ContractStatus(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    TERMINATED = "TERMINATED"


@dataclass
class Contract:
    project_id: str
    proposal_id: str
    freelancer_id: str
    client_id: str
    agreed_price: float
    estimated_days: int
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: ContractStatus = ContractStatus.ACTIVE
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: Optional[str] = None

    def __post_init__(self):
        if self.agreed_price <= 0:
            raise ValueError("Agreed price must be positive")
        if self.estimated_days <= 0:
            raise ValueError("Estimated days must be positive")

    def complete(self) -> None:
        if self.status != ContractStatus.ACTIVE:
            raise ValueError(f"Cannot complete contract with status '{self.status}'")
        self.status = ContractStatus.COMPLETED
        self.completed_at = datetime.utcnow().isoformat()

    def terminate(self) -> None:
        if self.status != ContractStatus.ACTIVE:
            raise ValueError(f"Cannot terminate contract with status '{self.status}'")
        self.status = ContractStatus.TERMINATED