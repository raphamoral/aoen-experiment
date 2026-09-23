from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.entities.project import Project, ProjectStatus


class IProjectRepository(ABC):
    """
    Porta de saída (driven port) para persistência de projetos.
    """

    @abstractmethod
    def save(self, project: Project) -> Project: ...

    @abstractmethod
    def find_by_id(self, project_id: UUID) -> Optional[Project]: ...

    @abstractmethod
    def find_by_status(self, status: ProjectStatus) -> List[Project]: ...

    @abstractmethod
    def find_all(self) -> List[Project]: ...