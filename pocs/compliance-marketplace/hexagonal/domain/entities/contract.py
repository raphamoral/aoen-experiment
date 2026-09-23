from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4


class ContractStatus(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    TERMINATED = "TERMINATED"


@dataclass
class Contract:
    project_id: UUID
    freelancer_id: UUID
    client_id: UUID
    proposal_id: UUID
    total_value: Decimal
    start_date: date
    end_date: date
    id: UUID = field(default_factory=uuid4)
    status: ContractStatus = ContractStatus.ACTIVE