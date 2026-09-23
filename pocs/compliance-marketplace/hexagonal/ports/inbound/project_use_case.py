from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from typing import List
from uuid import UUID

from domain.entities.project import Project
from domain.value_objects.compliance_area import ComplianceArea


class IProjectUseCase(ABC):
    """
    Porta de entrada (driving port) para operações de projeto.
    """

    @abstractmethod
    def create_project(
        self,
        title: str,
        description: str,
        client_id: UUID,
        required_areas: List[ComplianceArea],
        budget: Decimal,
        deadline: date,
    ) -> Project: ...

    @abstractmethod
    def get_project(self, project_id: UUID) -> Project: ...

    @abstractmethod
    def list_open_projects(self) -> List[Project]: ...

    @abstractmethod
    def cancel_project(self, project_id: UUID) -> Project: ...

    @abstractmethod
    def complete_project(self, project_id: UUID) -> Project: ...