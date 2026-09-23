from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from domain.entities.freelancer import Freelancer
from domain.exceptions import FreelancerNotFound, ProjectNotFound
from domain.services.matching_service import FreelancerMatchingService
from domain.value_objects.compliance_area import ComplianceArea
from domain.value_objects.expertise_level import ExpertiseLevel
from domain.value_objects.rate import HourlyRate
from ports.inbound.freelancer_use_case import IFreelancerUseCase
from ports.outbound.freelancer_repository import IFreelancerRepository
from ports.outbound.project_repository import IProjectRepository


class FreelancerApplicationService(IFreelancerUseCase):
    """
    Serviço de Aplicação: implementa a porta de entrada IFreelancerUseCase.
    Orquestra entidades de domínio e portas de saída; não contém lógica de negócio.
    """

    def __init__(
        self,
        freelancer_repo: IFreelancerRepository,
        project_repo: IProjectRepository,
        matching_service: FreelancerMatchingService,
    ) -> None:
        self._freelancer_repo = freelancer_repo
        self._project_repo = project_repo
        self._matching = matching_service

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
    ) -> Freelancer:
        freelancer = Freelancer(
            name=name,
            email=email,
            compliance_areas=compliance_areas,
            expertise_level=expertise_level,
            hourly_rate=HourlyRate(amount=hourly_rate, currency=currency),
            bio=bio,
            certifications=certifications,
        )
        return self._freelancer_repo.save(freelancer)

    def get_freelancer(self, freelancer_id: UUID) -> Freelancer:
        freelancer = self._freelancer_repo.find_by_id(freelancer_id)
        if not freelancer:
            raise FreelancerNotFound(freelancer_id)
        return freelancer

    def list_available_freelancers(
        self, area: Optional[ComplianceArea] = None
    ) -> List[Freelancer]:
        if area:
            return self._freelancer_repo.find_available_by_area(area)
        return self._freelancer_repo.find_available()

    def find_candidates_for_project(self, project_id: UUID) -> List[Freelancer]:
        project = self._project_repo.find_by_id(project_id)
        if not project:
            raise ProjectNotFound(project_id)
        available = self._freelancer_repo.find_available()
        return self._matching.rank_candidates(available, project)

    def update_availability(self, freelancer_id: UUID, available: bool) -> Freelancer:
        freelancer = self.get_freelancer(freelancer_id)
        if available:
            freelancer.make_available()
        else:
            freelancer.make_unavailable()
        return self._freelancer_repo.save(freelancer)

    def rate_freelancer(self, freelancer_id: UUID, rating: float) -> Freelancer:
        freelancer = self.get_freelancer(freelancer_id)
        freelancer.update_rating(rating)
        return self._freelancer_repo.save(freelancer)