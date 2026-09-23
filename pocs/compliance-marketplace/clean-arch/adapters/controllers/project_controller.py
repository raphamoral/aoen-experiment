from typing import List, Optional

from entities.project import Project
from use_cases.project.post_project import PostProject, PostProjectInput
from use_cases.project.list_projects import ListProjects
from adapters.presenters.schemas import ProjectCreateRequest, ProjectResponse


class ProjectController:
    def __init__(self, post_uc: PostProject, list_uc: ListProjects):
        self.post_uc = post_uc
        self.list_uc = list_uc

    def post(self, request: ProjectCreateRequest) -> ProjectResponse:
        project = self.post_uc.execute(
            PostProjectInput(
                title=request.title,
                description=request.description,
                budget=request.budget,
                compliance_areas=[a.value for a in request.compliance_areas],
                client_id=request.client_id,
            )
        )
        return self._to_response(project)

    def list_open(
        self,
        compliance_area: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[ProjectResponse]:
        return [self._to_response(p) for p in self.list_uc.execute(compliance_area, status)]

    def _to_response(self, p: Project) -> ProjectResponse:
        return ProjectResponse(
            id=p.id,
            title=p.title,
            description=p.description,
            budget=p.budget,
            compliance_areas=[a.value for a in p.compliance_areas],
            client_id=p.client_id,
            status=p.status.value,
            created_at=p.created_at,
        )