from typing import List, Optional

from entities.freelancer import Freelancer, ComplianceArea
from use_cases.ports.repositories import FreelancerRepository


class ListFreelancers:
    def __init__(self, repository: FreelancerRepository):
        self.repository = repository

    def execute(self, specialization: Optional[str] = None) -> List[Freelancer]:
        area: Optional[ComplianceArea] = None
        if specialization:
            try:
                area = ComplianceArea(specialization)
            except ValueError:
                raise ValueError(f"Invalid specialization: '{specialization}'")
        return self.repository.find_all(specialization=area)