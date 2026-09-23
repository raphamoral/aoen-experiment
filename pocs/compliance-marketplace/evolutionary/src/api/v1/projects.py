from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.schemas import ProjectCreate, ProjectResponse
from src.infrastructure.database import get_db
from src.infrastructure.repositories import AuditRepository, ProjectRepository
from src.services.project_service import ProjectService

router = APIRouter()


def _service(db: AsyncSession = Depends(get_db)) -> ProjectService:
    return ProjectService(
        repo=ProjectRepository(db),
        audit=AuditRepository(db),
    )


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    body: ProjectCreate,
    svc: ProjectService = Depends(_service),
):
    project = await svc.create_project(
        client_id=body.client_id,
        title=body.title,
        description=body.description,
        required_areas=body.required_areas,
        budget_brl=body.budget_brl,
    )
    return ProjectResponse(
        id=project.id,
        client_id=project.client_id,
        title=project.title,
        description=project.description,
        required_areas=project.required_areas,
        budget_brl=project.budget_brl,
        deadline=project.deadline,
        status=project.status,
        created_at=project.created_at,
    )


@router.post("/{project_id}/publish", response_model=ProjectResponse)
async def publish_project(
    project_id: str,
    actor_id: UUID,
    svc: ProjectService = Depends(_service),
):
    try:
        pid = UUID(project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID inválido")
    try:
        project = await svc.publish_project(pid, actor_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return ProjectResponse(
        id=project.id,
        client_id=project.client_id,
        title=project.title,
        description=project.description,
        required_areas=project.required_areas,
        budget_brl=project.budget_brl,
        deadline=project.deadline,
        status=project.status,
        created_at=project.created_at,
    )


@router.get("", response_model=List[ProjectResponse])
async def list_open_projects(svc: ProjectService = Depends(_service)):
    projects = await svc.list_open()
    return [
        ProjectResponse(
            id=p.id,
            client_id=p.client_id,
            title=p.title,
            description=p.description,
            required_areas=p.required_areas,
            budget_brl=p.budget_brl,
            deadline=p.deadline,
            status=p.status,
            created_at=p.created_at,
        )
        for p in projects
    ]