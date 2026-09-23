from typing import Dict, List, Optional
from uuid import UUID

from domain.entities.project import Project, ProjectStatus
from ports.outbound.project_repository import IProjectRepository


class InMemoryProjectRepository(IProjectRepository):
    """
    Adaptador de saída: implementa IProjectRepository em memória.
    """

    def __init__(self) -> None:
        self._store: Dict[UUID, Project] = {}

    def save(self, project: Project) -> Project:
        self._store[project.id] = project
        return project

    def find_by_id(self, project_id: UUID) -> Optional[Project]:
        return self._store.get(project_id)

    def find_by_status(self, status: ProjectStatus) -> List[Project]:
        return [p for p in self._store.values() if p.status == status]

    def find_all(self) -> List[Project]:
        return list(self._store.values())