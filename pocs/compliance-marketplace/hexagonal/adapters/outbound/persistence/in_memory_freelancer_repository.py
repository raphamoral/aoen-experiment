from typing import Dict, List, Optional
from uuid import UUID

from domain.entities.freelancer import Freelancer
from domain.value_objects.compliance_area import ComplianceArea
from ports.outbound.freelancer_repository import IFreelancerRepository


class InMemoryFreelancerRepository(IFreelancerRepository):
    """
    Adaptador de saída: implementa IFreelancerRepository em memória.
    Troque por SQLAlchemyFreelancerRepository sem tocar no domínio.
    """

    def __init__(self) -> None:
        self._store: Dict[UUID, Freelancer] = {}

    def save(self, freelancer: Freelancer) -> Freelancer:
        self._store[freelancer.id] = freelancer
        return freelancer

    def find_by_id(self, freelancer_id: UUID) -> Optional[Freelancer]:
        return self._store.get(freelancer_id)

    def find_all(self) -> List[Freelancer]:
        return list(self._store.values())

    def find_available(self) -> List[Freelancer]:
        return [f for f in self._store.values() if f.is_available]

    def find_available_by_area(self, area: ComplianceArea) -> List[Freelancer]:
        return [
            f for f in self._store.values()
            if f.is_available and f.specializes_in(area)
        ]