from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import ProjectStatus
from schemas import ProjectCreate, ProjectOut, ProjectUpdate
from services import project_service, tenant_service, billing_service

router = APIRouter()


def _get_active_tenant(tenant_id: str, db: Session):
    tenant = tenant_service.get_tenant(db, tenant_id)
    if not tenant or not tenant.is_active:
        raise HTTPException(status_code=404, detail="Tenant não encontrado.")
    return tenant


@router.post("/{tenant_id}", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    tenant_id: str,
    data: ProjectCreate,
    db: Session = Depends(get_db),
):
    tenant = _get_active_tenant(tenant_id, db)
    return project_service.create_project(db, tenant, data)


@router.get("/{tenant_id}", response_model=list[ProjectOut])
def list_projects(
    tenant_id: str,
    project_status: ProjectStatus | None = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    _get_active_tenant(tenant_id, db)
    return project_service.list_projects(db, tenant_id, project_status, skip, limit)


@router.get("/detail/{project_id}", response_model=ProjectOut)
def get_project(project_id: str, db: Session = Depends(get_db)):
    p = project_service.get_project(db, project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")
    return p


@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: str,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
):
    p = project_service.update_project(db, project_id, data)
    if not p:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")
    return p


@router.post("/{project_id}/open", response_model=ProjectOut)
def open_project(project_id: str, db: Session = Depends(get_db)):
    p = project_service.get_project(db, project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")
    if p.status != ProjectStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Apenas projetos em rascunho podem ser abertos.")
    return project_service.open_project(db, p)


@router.get("/{tenant_id}/billing/usage")
def get_usage(tenant_id: str, db: Session = Depends(get_db)):
    _get_active_tenant(tenant_id, db)
    return {
        "tenant_id": tenant_id,
        "summary": billing_service.get_tenant_usage_summary(db, tenant_id),
        "total_credits_consumed": billing_service.get_tenant_credit_balance(db, tenant_id),
    }