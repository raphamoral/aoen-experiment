from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import UUID

from entities.project import Project
from entities.value_objects import ComplianceSpecialty
from use_cases.ports import ClientRepository, ProjectRepository


@dataclass
class CreateProjectInput:
    client_id: str
    title: str
    description: str
    required_specialties: List[ComplianceSpecialty]
    budget_amount: str
    deadline: datetime


@dataclass
class CreateProjectOutput:
    project: Project


class CreateProjectUseCase:
    def __init__(self, project_repo: ProjectRepository, client_repo: ClientRepository) -> None:
        self._project_repo = project_repo
        self._client_repo = client_repo

    def execute(self, input_data: CreateProjectInput) -> CreateProjectOutput:
        client_id = UUID(input_data.client_id)
        client = self._client_repo.find_by_id(client_id)
        if not client:
            raise ValueError(f"Client not found: {input_data.client_id}")

        project = Project.create(
            client_id=client_id,
            title=input_data.title,
            description=input_data.description,
            required_specialties=input_data.required_specialties,
            budget_amount=input_data.budget_amount,
            deadline=input_data.deadline,
        )
        saved = self._project_repo.save(project)
        return CreateProjectOutput(project=saved)