from sqlalchemy.orm import Session

from models import Tenant
from schemas import TenantCreate


def create_tenant(db: Session, data: TenantCreate) -> Tenant:
    tenant = Tenant(**data.model_dump())
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


def get_tenant(db: Session, tenant_id: str) -> Tenant | None:
    return db.query(Tenant).filter(Tenant.id == tenant_id).first()


def get_tenant_by_slug(db: Session, slug: str) -> Tenant | None:
    return db.query(Tenant).filter(Tenant.slug == slug).first()


def list_tenants(db: Session) -> list[Tenant]:
    return db.query(Tenant).filter(Tenant.is_active == True).all()


def update_tenant_config(db: Session, tenant_id: str, config_patch: dict) -> Tenant | None:
    tenant = get_tenant(db, tenant_id)
    if not tenant:
        return None
    existing = tenant.config or {}
    existing.update(config_patch)
    tenant.config = existing
    db.commit()
    db.refresh(tenant)
    return tenant