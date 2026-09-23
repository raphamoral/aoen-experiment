from sqlalchemy.orm import Session

from models import Freelancer
from schemas import FreelancerCreate, FreelancerUpdate


def create_freelancer(db: Session, tenant_id: str, data: FreelancerCreate) -> Freelancer:
    freelancer = Freelancer(
        tenant_id=tenant_id,
        **data.model_dump(),
    )
    db.add(freelancer)
    db.commit()
    db.refresh(freelancer)
    return freelancer


def get_freelancer(db: Session, freelancer_id: str) -> Freelancer | None:
    return db.query(Freelancer).filter(Freelancer.id == freelancer_id).first()


def list_freelancers(
    db: Session,
    tenant_id: str,
    domain: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[Freelancer]:
    q = db.query(Freelancer).filter(
        Freelancer.tenant_id == tenant_id,
        Freelancer.is_active == True,
    )
    if domain:
        # JSON contains — SQLite/Postgres compatible via JSON path
        q = q.filter(Freelancer.domains.contains([domain]))
    return q.offset(skip).limit(limit).all()


def update_freelancer(
    db: Session, freelancer_id: str, data: FreelancerUpdate
) -> Freelancer | None:
    freelancer = get_freelancer(db, freelancer_id)
    if not freelancer:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(freelancer, field, value)
    db.commit()
    db.refresh(freelancer)
    return freelancer


def deactivate_freelancer(db: Session, freelancer_id: str) -> bool:
    freelancer = get_freelancer(db, freelancer_id)
    if not freelancer:
        return False
    freelancer.is_active = False
    db.commit()
    return True