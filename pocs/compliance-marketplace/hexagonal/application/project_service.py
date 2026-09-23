from datetime import date
from decimal import Decimal
from typing import List
from uuid import UUID

from domain.entities.project import Project, ProjectStatus
from domain.exceptions import ProjectNotFound
from domain.value_objects.compliance_area import ComplianceArea
from ports.inbound.project_use_case import IProjectUseCase
from ports.outbound.project_repository import IProjectRepository


class ProjectApplicationService(IProjectUseCase):
    """
    Serviço de Aplicação: implementa a porta de entrada IProjectUseCase.
    """

    def __init__(self, project_repo: IProjectRepository) -> None:
        self._project_repo = project_repo

    def create_project(
        self,
        title: str,
        description: str,
        client_id: UUID,
        required_areas: List[ComplianceArea],
        budget: Decimal,
        deadline: date,
    ) -> Project:
        project = Project(
            title=title,
            description=description,
            client_id=client_id,
            required_areas=required_areas,
            budget=budget,
            deadline=deadline,
        )
        return self._project_repo.save(project)

    def get_project(self, project_id: UUID) -> Project:
        project = self._project_repo.find_by_id(project_id)
        if not project:
            raise ProjectNotFound(project_id)
        return project

    def list_open_projects(self) -> List[Project]:
        return self._project_repo.find_by_status(ProjectStatus.OPEN)

    def cancel_project(self, project_id: UUID) -> Project:
        project = self.get_project(project_id)
        project.cancel()
        return self._project_repo.save(project)

    def complete_project(self, project_id: UUID) -> Project:
        project = self.get_project(project_id)
        project.complete()
        return self._project_repo.save(project)