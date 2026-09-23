from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import FreelancerCreate, FreelancerOut, FreelancerUpdate
from services import freelancer_service, tenant_service

router = APIRouter()


def _get_active_tenant(tenant_id: str, db: Session):
    tenant = tenant_service.get_tenant(db, tenant_id)
    if not tenant or not tenant.is_active:
        raise HTTPException(status_code=404, detail="Tenant não encontrado.")
    return tenant


@router.post("/{tenant_id}", response_model=FreelancerOut, status_code=status.HTTP_201_CREATED)
def create_freelancer(
    tenant_id: str,
    data: FreelancerCreate,
    db: Session = Depends(get_db),
):
    _get_active_tenant(tenant_id, db)
    return freelancer_service.create_freelancer(db, tenant_id, data)


@router.get("/{tenant_id}", response_model=list[FreelancerOut])
def list_freelancers(
    tenant_id: str,
    domain: str | None = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    _get_active_tenant(tenant_id, db)
    return freelancer_service.list_freelancers(db, tenant_id, domain, skip, limit)


@router.get("/detail/{freelancer_id}", response_model=FreelancerOut)
def get_freelancer(freelancer_id: str, db: Session = Depends(get_db)):
    f = freelancer_service.get_freelancer(db, freelancer_id)
    if not f:
        raise HTTPException(status_code=404, detail="Freelancer não encontrado.")
    return f


@router.patch("/{freelancer_id}", response_model=FreelancerOut)
def update_freelancer(
    freelancer_id: str,
    data: FreelancerUpdate,
    db: Session = Depends(get_db),
):
    f = freelancer_service.update_freelancer(db, freelancer_id, data)
    if not f:
        raise HTTPException(status_code=404, detail="Freelancer não encontrado.")
    return f


@router.delete("/{freelancer_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_freelancer(freelancer_id: str, db: Session = Depends(get_db)):
    if not freelancer_service.deactivate_freelancer(db, freelancer_id):
        raise HTTPException(status_code=404, detail="Freelancer não encontrado.")