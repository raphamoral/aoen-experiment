from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List
from uuid import UUID

from domain.entities.proposal import Proposal


class IProposalUseCase(ABC):
    """
    Porta de entrada (driving port) para operações de proposta.
    """

    @abstractmethod
    def submit_proposal(
        self,
        project_id: UUID,
        freelancer_id: UUID,
        proposed_rate: Decimal,
        cover_letter: str,
        estimated_hours: int,
    ) -> Proposal: ...

    @abstractmethod
    def accept_proposal(self, proposal_id: UUID) -> Proposal: ...

    @abstractmethod
    def reject_proposal(self, proposal_id: UUID) -> Proposal: ...

    @abstractmethod
    def withdraw_proposal(self, proposal_id: UUID) -> Proposal: ...

    @abstractmethod
    def list_proposals_for_project(self, project_id: UUID) -> List[Proposal]: ...

    @abstractmethod
    def list_proposals_by_freelancer(self, freelancer_id: UUID) -> List[Proposal]: ...