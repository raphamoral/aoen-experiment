from dataclasses import dataclass
from typing import List

from entities.freelancer import Freelancer, ComplianceArea
from use_cases.ports.repositories import FreelancerRepository


@dataclass
class CreateFreelancerInput:
    name: str
    email: str
    specializations: List[str]
    hourly_rate: float
    bio: str


class CreateFreelancer:
    def __init__(self, repository: FreelancerRepository):
        self.repository = repository

    def execute(self, input: CreateFreelancerInput) -> Freelancer:
        if self.repository.find_by_email(input.email):
            raise ValueError(f"Email '{input.email}' is already registered")

        try:
            areas = [ComplianceArea(s) for s in input.specializations]
        except ValueError as e:
            raise ValueError(f"Invalid specialization: {e}")

        freelancer = Freelancer(
            name=input.name,
            email=input.email,
            specializations=areas,
            hourly_rate=input.hourly_rate,
            bio=input.bio,
        )
        return self.repository.save(freelancer)