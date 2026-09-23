from typing import List

from domain.entities.freelancer import Freelancer
from domain.entities.project import Project
from domain.exceptions import IncompatibleExpertise


class FreelancerMatchingService:
    """
    Serviço de Domínio puro: toda lógica de matching vive aqui,
    sem nenhuma dependência de infraestrutura.

    Regras de negócio:
    - Freelancer deve estar disponível.
    - Freelancer deve cobrir TODAS as áreas de compliance exigidas.
    - Ranking: maior rating primeiro; menor taxa horária como desempate.
    """

    def is_eligible(self, freelancer: Freelancer, project: Project) -> bool:
        if not freelancer.is_available:
            return False
        return all(freelancer.specializes_in(area) for area in project.required_areas)

    def rank_candidates(
        self, freelancers: List[Freelancer], project: Project
    ) -> List[Freelancer]:
        eligible = [f for f in freelancers if self.is_eligible(f, project)]
        return sorted(
            eligible,
            key=lambda f: (-(f.rating or 0.0), f.hourly_rate.amount),
        )

    def assert_eligible(self, freelancer: Freelancer, project: Project) -> None:
        if not self.is_eligible(freelancer, project):
            missing = [
                area.value
                for area in project.required_areas
                if not freelancer.specializes_in(area)
            ]
            raise IncompatibleExpertise(
                f"Freelancer '{freelancer.name}' não cobre as áreas: {missing}"
            )