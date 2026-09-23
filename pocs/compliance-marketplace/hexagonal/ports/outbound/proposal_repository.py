from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.entities.proposal import Proposal


class IProposalRepository(ABC):
    """
    Porta de saída (driven port) para persistência de propostas.
    """

    @abstractmethod
    def save(self, proposal: Proposal) -> Proposal: ...

    @abstractmethod
    def find_by_id(self, proposal_id: UUID) -> Optional[Proposal]: ...

    @abstractmethod
    def find_by_project(self, project_id: UUID) -> List[Proposal]: ...

    @abstractmethod
    def find_by_freelancer(self, freelancer_id: UUID) -> List[Proposal]: ...