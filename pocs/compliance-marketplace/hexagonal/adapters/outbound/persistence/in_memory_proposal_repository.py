from typing import Dict, List, Optional
from uuid import UUID

from domain.entities.proposal import Proposal
from ports.outbound.proposal_repository import IProposalRepository


class InMemoryProposalRepository(IProposalRepository):
    """
    Adaptador de saída: implementa IProposalRepository em memória.
    """

    def __init__(self) -> None:
        self._store: Dict[UUID, Proposal] = {}

    def save(self, proposal: Proposal) -> Proposal:
        self._store[proposal.id] = proposal
        return proposal

    def find_by_id(self, proposal_id: UUID) -> Optional[Proposal]:
        return self._store.get(proposal_id)

    def find_by_project(self, project_id: UUID) -> List[Proposal]:
        return [p for p in self._store.values() if p.project_id == project_id]

    def find_by_freelancer(self, freelancer_id: UUID) -> List[Proposal]:
        return [p for p in self._store.values() if p.freelancer_id == freelancer_id]