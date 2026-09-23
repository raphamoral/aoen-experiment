from entities.freelancer import Freelancer
from use_cases.ports.repositories import FreelancerRepository


class GetFreelancer:
    def __init__(self, repository: FreelancerRepository):
        self.repository = repository

    def execute(self, freelancer_id: str) -> Freelancer:
        freelancer = self.repository.find_by_id(freelancer_id)
        if not freelancer:
            raise ValueError(f"Freelancer '{freelancer_id}' not found")
        return freelancer