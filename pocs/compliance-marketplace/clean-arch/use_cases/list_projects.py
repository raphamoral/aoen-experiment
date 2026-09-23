from dataclasses import dataclass
from typing import List

from entities.project import Project
from use_cases.ports import ProjectRepository


@dataclass
class ListOpenProjectsInput:
    skip: int = 0
    limit: int = 20


@dataclass
class ListOpenProjectsOutput:
    projects: List[Project]
    total: int


class ListOpenProjectsUseCase:
    def __init__(self, project_repo: ProjectRepository) -> None:
        self._repo = project_repo

    def execute(self, input_data: ListOpenProjectsInput) -> ListOpenProjectsOutput:
        projects = self._repo.list_open(skip=input_data.skip, limit=input_data.limit)
        return ListOpenProjectsOutput(projects=projects, total=len(projects))