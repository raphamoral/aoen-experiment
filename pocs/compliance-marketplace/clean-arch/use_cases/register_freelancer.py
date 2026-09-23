from dataclasses import dataclass
from typing import List, Optional

from entities.freelancer import Freelancer
from entities.value_objects import ComplianceSpecialty
from use_cases.ports import FreelancerRepository


@dataclass
class RegisterFreelancerInput:
    name: str
    email: str
    specialties: List[ComplianceSpecialty]
    hourly_rate_amount: str
    bio: str
    years_of_experience: int
    certifications: Optional[List[str]] = None


@dataclass
class RegisterFreelancerOutput:
    freelancer: Freelancer


class RegisterFreelancerUseCase:
    def __init__(self, freelancer_repo: FreelancerRepository) -> None:
        self._repo = freelancer_repo

    def execute(self, input_data: RegisterFreelancerInput) -> RegisterFreelancerOutput:
        existing = self._repo.find_by_email(input_data.email)
        if existing:
            raise ValueError(f"Email already registered: {input_data.email}")

        freelancer = Freelancer.create(
            name=input_data.name,
            email=input_data.email,
            specialties=input_data.specialties,
            hourly_rate_amount=input_data.hourly_rate_amount,
            bio=input_data.bio,
            years_of_experience=input_data.years_of_experience,
            certifications=input_data.certifications,
        )
        saved = self._repo.save(freelancer)
        return RegisterFreelancerOutput(freelancer=saved)