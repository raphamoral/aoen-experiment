from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from domain.exceptions import InvalidProposalTransition


class ProposalStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"


@dataclass
class Proposal:
    project_id: UUID
    freelancer_id: UUID
    proposed_rate: Decimal
    cover_letter: str
    estimated_hours: int
    id: UUID = field(default_factory=uuid4)
    status: ProposalStatus = ProposalStatus.PENDING

    @property
    def total_cost(self) -> Decimal:
        return self.proposed_rate * self.estimated_hours

    def accept(self) -> None:
        if self.status != ProposalStatus.PENDING:
            raise InvalidProposalTransition(
                f"Apenas propostas PENDING podem ser aceitas. Status atual: {self.status}"
            )
        self.status = ProposalStatus.ACCEPTED

    def reject(self) -> None:
        if self.status != ProposalStatus.PENDING:
            raise InvalidProposalTransition(
                f"Apenas propostas PENDING podem ser rejeitadas. Status atual: {self.status}"
            )
        self.status = ProposalStatus.REJECTED

    def withdraw(self) -> None:
        if self.status != ProposalStatus.PENDING:
            raise InvalidProposalTransition(
                f"Apenas propostas PENDING podem ser retiradas. Status atual: {self.status}"
            )
        self.status = ProposalStatus.WITHDRAWN