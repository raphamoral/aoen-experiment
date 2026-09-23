from dataclasses import dataclass, field
from typing import List
from enum import Enum
import uuid


class ComplianceArea(str, Enum):
    LGPD = "LGPD"
    GDPR = "GDPR"
    SOX = "SOX"
    ISO_27001 = "ISO_27001"
    PCI_DSS = "PCI_DSS"
    BACEN = "BACEN"
    CVM = "CVM"
    HIPAA = "HIPAA"
    COBIT = "COBIT"
    FEBRABAN = "FEBRABAN"


@dataclass
class Freelancer:
    name: str
    email: str
    specializations: List[ComplianceArea]
    hourly_rate: float
    bio: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    rating: float = 0.0
    total_reviews: int = 0
    is_active: bool = True

    def __post_init__(self):
        self._validate()

    def _validate(self):
        if not self.name or len(self.name.strip()) < 2:
            raise ValueError("Name must have at least 2 characters")
        if "@" not in self.email or "." not in self.email:
            raise ValueError("Invalid email address")
        if self.hourly_rate <= 0:
            raise ValueError("Hourly rate must be positive")
        if not self.specializations:
            raise ValueError("At least one specialization is required")

    def add_review(self, score: float) -> None:
        if not 1.0 <= score <= 5.0:
            raise ValueError("Score must be between 1.0 and 5.0")
        total = self.rating * self.total_reviews + score
        self.total_reviews += 1
        self.rating = round(total / self.total_reviews, 2)

    def deactivate(self) -> None:
        self.is_active = False