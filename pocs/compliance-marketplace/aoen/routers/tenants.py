from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import TenantCreate, TenantOut
from services import tenant_service

router = APIRouter()


@router.post("/", response_model=TenantOut, status_code=status.HTTP_201_CREATED)
def create_tenant(data: TenantCreate, db: Session = Depends(get_db)):
    if tenant_service.get_tenant_by_slug(db, data.slug):
        raise HTTPException(status_code=400, detail="Slug já em uso.")
    return tenant_service.create_tenant(db, data)


@router.get("/", response_model=list[TenantOut])
def list_tenants(db: Session = Depends(get_db)):
    return tenant_service.list_tenants(db)


@router.get("/{tenant_id}", response_model=TenantOut)
def get_tenant(tenant_id: str, db: Session = Depends(get_db)):
    tenant = tenant_service.get_tenant(db, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado.")
    return tenant


@router.patch("/{tenant_id}/config", response_model=TenantOut)
def update_config(tenant_id: str, config_patch: dict, db: Session = Depends(get_db)):
    tenant = tenant_service.update_tenant_config(db, tenant_id, config_patch)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado.")
    return tenant