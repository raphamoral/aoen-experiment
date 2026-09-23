from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from domain.exceptions import InvalidProjectTransition
from domain.value_objects.compliance_area import ComplianceArea


class ProjectStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


@dataclass
class Project:
    title: str
    description: str
    client_id: UUID
    required_areas: List[ComplianceArea]
    budget: Decimal
    deadline: date
    id: UUID = field(default_factory=uuid4)
    status: ProjectStatus = ProjectStatus.OPEN
    assigned_freelancer_id: Optional[UUID] = None

    def assign_freelancer(self, freelancer_id: UUID) -> None:
        if self.status != ProjectStatus.OPEN:
            raise InvalidProjectTransition(
                f"Apenas projetos OPEN podem receber um freelancer. Status atual: {self.status}"
            )
        self.assigned_freelancer_id = freelancer_id
        self.status = ProjectStatus.IN_PROGRESS

    def complete(self) -> None:
        if self.status != ProjectStatus.IN_PROGRESS:
            raise InvalidProjectTransition(
                f"Apenas projetos IN_PROGRESS podem ser concluídos. Status atual: {self.status}"
            )
        self.status = ProjectStatus.COMPLETED

    def cancel(self) -> None:
        if self.status == ProjectStatus.COMPLETED:
            raise InvalidProjectTransition("Projetos concluídos não podem ser cancelados.")
        self.status = ProjectStatus.CANCELLED