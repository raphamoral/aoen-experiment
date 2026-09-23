from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from entities.project import Project
from entities.value_objects import ComplianceSpecialty, Money, ProjectStatus
from frameworks.database.models import ProjectModel
from use_cases.ports import ProjectRepository


class SQLAlchemyProjectRepository(ProjectRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, project: Project) -> Project:
        model = self._session.get(ProjectModel, str(project.id))
        if model:
            self._update_model(model, project)
        else:
            model = self._to_model(project)
            self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def find_by_id(self, project_id: UUID) -> Optional[Project]:
        model = self._session.get(ProjectModel, str(project_id))
        return self._to_entity(model) if model else None

    def list_open(self, skip: int = 0, limit: int = 20) -> List[Project]:
        models = (
            self._session.query(ProjectModel)
            .filter(ProjectModel.status == ProjectStatus.OPEN.value)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def list_by_client(self, client_id: UUID) -> List[Project]:
        models = (
            self._session.query(ProjectModel)
            .filter(ProjectModel.client_id == str(client_id))
            .all()
        )
        return [self._to_entity(m) for m in models]

    @staticmethod
    def _to_model(project: Project) -> ProjectModel:
        return ProjectModel(
            id=str(project.id),
            client_id=str(project.client_id),
            title=project.title,
            description=project.description,
            required_specialties=",".join(s.value for s in project.required_specialties),
            budget_amount=str(project.budget.amount),
            budget_currency=project.budget.currency,
            deadline=project.deadline,
            status=project.status.value,
            created_at=project.created_at,
        )

    @staticmethod
    def _update_model(model: ProjectModel, project: Project) -> None:
        model.title = project.title
        model.description = project.description
        model.required_specialties = ",".join(s.value for s in project.required_specialties)
        model.budget_amount = str(project.budget.amount)
        model.status = project.status.value

    @staticmethod
    def _to_entity(model: ProjectModel) -> Project:
        specialties = [ComplianceSpecialty(s) for s in model.required_specialties.split(",") if s]
        return Project(
            id=UUID(model.id),
            client_id=UUID(model.client_id),
            title=model.title,
            description=model.description,
            required_specialties=specialties,
            budget=Money(Decimal(model.budget_amount), model.budget_currency),
            deadline=model.deadline,
            status=ProjectStatus(model.status),
            created_at=model.created_at,
        )