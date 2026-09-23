from dataclasses import dataclass
from typing import List

from entities.project import Project
from entities.freelancer import ComplianceArea
from use_cases.ports.repositories import ProjectRepository, ClientRepository


@dataclass
class PostProjectInput:
    title: str
    description: str
    budget: float
    compliance_areas: List[str]
    client_id: str


class PostProject:
    def __init__(self, project_repo: ProjectRepository, client_repo: ClientRepository):
        self.project_repo = project_repo
        self.client_repo = client_repo

    def execute(self, input: PostProjectInput) -> Project:
        if not self.client_repo.find_by_id(input.client_id):
            raise ValueError(f"Client '{input.client_id}' not found")

        try:
            areas = [ComplianceArea(a) for a in input.compliance_areas]
        except ValueError as e:
            raise ValueError(f"Invalid compliance area: {e}")

        project = Project(
            title=input.title,
            description=input.description,
            budget=input.budget,
            compliance_areas=areas,
            client_id=input.client_id,
        )
        return self.project_repo.save(project)