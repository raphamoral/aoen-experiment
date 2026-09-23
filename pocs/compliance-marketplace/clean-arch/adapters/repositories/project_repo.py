from typing import List, Optional
from sqlalchemy.orm import Session

from entities.project import Project, ProjectStatus
from entities.freelancer import ComplianceArea
from use_cases.ports.repositories import ProjectRepository
from adapters.repositories.orm_models import ProjectModel


class SQLAlchemyProjectRepository(ProjectRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, project: Project) -> Project:
        model = ProjectModel(
            id=project.id,
            title=project.title,
            description=project.description,
            budget=project.budget,
            compliance_areas=[a.value for a in project.compliance_areas],
            client_id=project.client_id,
            status=project.status.value,
            created_at=project.created_at,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def find_by_id(self, id: str) -> Optional[Project]:
        model = self.session.query(ProjectModel).filter_by(id=id).first()
        return self._to_entity(model) if model else None

    def find_by_status(self, status: ProjectStatus) -> List[Project]:
        models = self.session.query(ProjectModel).filter_by(status=status.value).all()
        return [self._to_entity(m) for m in models]

    def find_by_compliance_area(
        self, area: ComplianceArea, status: Optional[ProjectStatus] = None
    ) -> List[Project]:
        query = self.session.query(ProjectModel)
        if status:
            query = query.filter_by(status=status.value)
        return [
            self._to_entity(m)
            for m in query.all()
            if area.value in (m.compliance_areas or [])
        ]

    def find_by_client(self, client_id: str) -> List[Project]:
        models = self.session.query(ProjectModel).filter_by(client_id=client_id).all()
        return [self._to_entity(m) for m in models]

    def update(self, project: Project) -> Project:
        model = self.session.query(ProjectModel).filter_by(id=project.id).first()
        if not model:
            raise ValueError(f"Project '{project.id}' not found for update")
        model.title = project.title
        model.description = project.description
        model.budget = project.budget
        model.status = project.status.value
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def _to_entity(self, model: ProjectModel) -> Project:
        return Project(
            id=model.id,
            title=model.title,
            description=model.description,
            budget=model.budget,
            compliance_areas=[ComplianceArea(a) for a in model.compliance_areas],
            client_id=model.client_id,
            status=ProjectStatus(model.status),
            created_at=model.created_at,
        )