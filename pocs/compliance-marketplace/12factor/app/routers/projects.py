import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_freelancer
from app.models import Freelancer, Project, ProjectStatus
from app.schemas import ProjectCreate, ProjectResponse, ProjectUpdate

router = APIRouter()


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    project = Project(**payload.model_dump())
    db.add(project)
    await db.flush()
    await db.refresh(project)
    return ProjectResponse.model_validate(project)


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    domain: str | None = Query(default=None),
    status: ProjectStatus | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> list[ProjectResponse]:
    query = select(Project).offset(skip).limit(limit)
    if domain:
        query = query.where(Project.domain == domain)
    if status:
        query = query.where(Project.status == status)
    result = await db.execute(query)
    return [ProjectResponse.model_validate(p) for p in result.scalars().all()]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> ProjectResponse:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return ProjectResponse.model_validate(project)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    payload: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(project, field, value)
    await db.flush()
    await db.refresh(project)
    return ProjectResponse.model_validate(project)


@router.post("/{project_id}/assign", response_model=ProjectResponse)
async def assign_freelancer(
    project_id: uuid.UUID,
    current: Freelancer = Depends(get_current_freelancer),
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    if project.status != ProjectStatus.OPEN:
        raise HTTPException(status_code=409, detail="Projeto não está disponível")
    project.freelancer_id = current.id
    project.status = ProjectStatus.IN_PROGRESS
    await db.flush()
    await db.refresh(project)
    return ProjectResponse.model_validate(project)