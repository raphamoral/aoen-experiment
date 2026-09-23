from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from domain.entities.freelancer import Freelancer
from domain.value_objects.compliance_area import ComplianceArea
from domain.value_objects.expertise_level import ExpertiseLevel


class IFreelancerUseCase(ABC):
    """
    Porta de entrada (driving port) para operações de freelancer.
    Define o contrato que os adaptadores de entrada (HTTP, CLI, etc.)
    devem usar para interagir com o domínio.
    """

    @abstractmethod
    def register_freelancer(
        self,
        name: str,
        email: str,
        compliance_areas: List[ComplianceArea],
        expertise_level: ExpertiseLevel,
        hourly_rate: Decimal,
        currency: str,
        bio: str,
        certifications: List[str],
    ) -> Freelancer: ...

    @abstractmethod
    def get_freelancer(self, freelancer_id: UUID) -> Freelancer: ...

    @abstractmethod
    def list_available_freelancers(
        self, area: Optional[ComplianceArea] = None
    ) -> List[Freelancer]: ...

    @abstractmethod
    def find_candidates_for_project(self, project_id: UUID) -> List[Freelancer]: ...

    @abstractmethod
    def update_availability(self, freelancer_id: UUID, available: bool) -> Freelancer: ...

    @abstractmethod
    def rate_freelancer(self, freelancer_id: UUID, rating: float) -> Freelancer: ...