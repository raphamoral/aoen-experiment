from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.entities.freelancer import Freelancer
from domain.value_objects.compliance_area import ComplianceArea


class IFreelancerRepository(ABC):
    """
    Porta de saída (driven port) para persistência de freelancers.
    O domínio depende desta abstração; a infraestrutura a implementa.
    """

    @abstractmethod
    def save(self, freelancer: Freelancer) -> Freelancer: ...

    @abstractmethod
    def find_by_id(self, freelancer_id: UUID) -> Optional[Freelancer]: ...

    @abstractmethod
    def find_all(self) -> List[Freelancer]: ...

    @abstractmethod
    def find_available(self) -> List[Freelancer]: ...

    @abstractmethod
    def find_available_by_area(self, area: ComplianceArea) -> List[Freelancer]: ...