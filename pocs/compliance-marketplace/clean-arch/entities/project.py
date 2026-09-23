from dataclasses import dataclass, field
from typing import List
from enum import Enum
from datetime import datetime
import uuid

from entities.freelancer import ComplianceArea


class ProjectStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


@dataclass
class Project:
    title: str
    description: str
    budget: float
    compliance_areas: List[ComplianceArea]
    client_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: ProjectStatus = ProjectStatus.OPEN
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def __post_init__(self):
        self._validate()

    def _validate(self):
        if not self.title or len(self.title.strip()) < 3:
            raise ValueError("Title must have at least 3 characters")
        if self.budget <= 0:
            raise ValueError("Budget must be positive")
        if not self.compliance_areas:
            raise ValueError("At least one compliance area is required")

    def start(self) -> None:
        if self.status != ProjectStatus.OPEN:
            raise ValueError(f"Cannot start project with status '{self.status}'")
        self.status = ProjectStatus.IN_PROGRESS

    def complete(self) -> None:
        if self.status != ProjectStatus.IN_PROGRESS:
            raise ValueError(f"Cannot complete project with status '{self.status}'")
        self.status = ProjectStatus.COMPLETED

    def cancel(self) -> None:
        if self.status == ProjectStatus.COMPLETED:
            raise ValueError("Cannot cancel a completed project")
        self.status = ProjectStatus.CANCELLED