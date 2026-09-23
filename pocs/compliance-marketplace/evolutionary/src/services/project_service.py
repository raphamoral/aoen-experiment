from uuid import UUID, uuid4

from src.domain.models import AuditEvent, ComplianceArea, Project, ProjectStatus
from src.infrastructure.repositories import AuditRepository, ProjectRepository


class ProjectService:
    def __init__(self, repo: ProjectRepository, audit: AuditRepository):
        self.repo = repo
        self.audit = audit

    async def create_project(
        self,
        client_id: UUID,
        title: str,
        description: str,
        required_areas: list[ComplianceArea],
        budget_brl: float,
    ) -> Project:
        project = Project(
            id=uuid4(),
            client_id=client_id,
            title=title,
            description=description,
            required_areas=required_areas,
            budget_brl=budget_brl,
        )
        await self.repo.save(project)
        await self.audit.record(
            AuditEvent(
                entity_type="project",
                entity_id=project.id,
                action="created",
                actor_id=client_id,
                payload={"title": title, "areas": [a.value for a in required_areas]},
            )
        )
        return project

    async def publish_project(self, project_id: UUID, actor_id: UUID) -> Project:
        project = await self.repo.find_by_id(project_id)
        if not project:
            raise ValueError(f"Projeto {project_id} não encontrado")
        project.publish()
        await self.repo.update_status(project_id, ProjectStatus.OPEN)
        await self.audit.record(
            AuditEvent(
                entity_type="project",
                entity_id=project_id,
                action="published",
                actor_id=actor_id,
                payload={},
            )
        )
        return project

    async def list_open(self) -> list[Project]:
        return await self.repo.list_open()

    async def get(self, project_id: UUID) -> Project | None:
        return await self.repo.find_by_id(project_id)