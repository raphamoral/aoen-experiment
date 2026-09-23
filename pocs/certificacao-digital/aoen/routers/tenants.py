"""
Endpoints de gerenciamento de tenants — thin router.
Toda lógica vive em TenantService.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from services.certificate_service import get_key_store
from services.tenant_service import TenantService

router = APIRouter(prefix="/tenants", tags=["tenants"])


class TenantCreateRequest(BaseModel):
    slug: str
    name: str
    config: dict | None = None


class TenantResponse(BaseModel):
    id: str
    slug: str
    name: str
    is_active: bool
    public_key_pem: str | None

    model_config = {"from_attributes": True}


class TenantCreateResponse(TenantResponse):
    private_key_pem: str  # retornado UMA VEZ na criação; nunca mais exposto


@router.post("/", response_model=TenantCreateResponse, status_code=status.HTTP_201_CREATED)
def create_tenant(body: TenantCreateRequest, db: Session = Depends(get_db)):
    svc = TenantService(db, get_key_store())
    try:
        tenant, private_pem = svc.create(slug=body.slug, name=body.name, config=body.config)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return TenantCreateResponse(
        id=tenant.id,
        slug=tenant.slug,
        name=tenant.name,
        is_active=tenant.is_active,
        public_key_pem=tenant.public_key_pem,
        private_key_pem=private_pem,
    )


@router.get("/", response_model=list[TenantResponse])
def list_tenants(db: Session = Depends(get_db)):
    svc = TenantService(db, get_key_store())
    return svc.list_all()


@router.get("/{tenant_id}", response_model=TenantResponse)
def get_tenant(tenant_id: str, db: Session = Depends(get_db)):
    svc = TenantService(db, get_key_store())
    tenant = svc.get_by_id(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado.")
    return tenant


@router.patch("/{tenant_id}/config", response_model=TenantResponse)
def update_tenant_config(tenant_id: str, config_patch: dict, db: Session = Depends(get_db)):
    svc = TenantService(db, get_key_store())
    try:
        return svc.update_config(tenant_id, config_patch)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))