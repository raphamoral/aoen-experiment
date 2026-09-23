from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from config import PLAN_LIMITS
from models import Project, ProjectStatus, Tenant
from schemas import ProjectCreate, ProjectUpdate


def _check_project_limit(db: Session, tenant: Tenant) -> None:
    plan = tenant.plan or "starter"
    limit = PLAN_LIMITS.get(plan, PLAN_LIMITS["starter"])["max_open_projects"]
    if limit == -1:
        return
    open_count = (
        db.query(Project)
        .filter(
            Project.tenant_id == tenant.id,
            Project.status == ProjectStatus.OPEN,
        )
        .count()
    )
    if open_count >= limit:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Plano '{plan}' permite no máximo {limit} projetos abertos.",
        )


def create_project(db: Session, tenant: Tenant, data: ProjectCreate) -> Project:
    _check_project_limit(db, tenant)
    project = Project(tenant_id=tenant.id, **data.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def get_project(db: Session, project_id: str) -> Project | None:
    return db.query(Project).filter(Project.id == project_id).first()


def list_projects(
    db: Session,
    tenant_id: str,
    status: ProjectStatus | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[Project]:
    q = db.query(Project).filter(Project.tenant_id == tenant_id)
    if status:
        q = q.filter(Project.status == status)
    return q.order_by(Project.created_at.desc()).offset(skip).limit(limit).all()


def update_project(
    db: Session, project_id: str, data: ProjectUpdate
) -> Project | None:
    project = get_project(db, project_id)
    if not project:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


def open_project(db: Session, project: Project) -> Project:
    project.status = ProjectStatus.OPEN
    db.commit()
    db.refresh(project)
    return project