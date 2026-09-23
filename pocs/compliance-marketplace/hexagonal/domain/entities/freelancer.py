from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID, uuid4

from domain.value_objects.compliance_area import ComplianceArea
from domain.value_objects.expertise_level import ExpertiseLevel
from domain.value_objects.rate import HourlyRate


@dataclass
class Freelancer:
    name: str
    email: str
    compliance_areas: List[ComplianceArea]
    expertise_level: ExpertiseLevel
    hourly_rate: HourlyRate
    bio: str
    certifications: List[str] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)
    is_available: bool = True
    rating: Optional[float] = None

    def make_available(self) -> None:
        self.is_available = True

    def make_unavailable(self) -> None:
        self.is_available = False

    def update_rating(self, new_rating: float) -> None:
        if not 0.0 <= new_rating <= 5.0:
            raise ValueError("Rating deve estar entre 0.0 e 5.0.")
        self.rating = new_rating

    def specializes_in(self, area: ComplianceArea) -> bool:
        return area in self.compliance_areas