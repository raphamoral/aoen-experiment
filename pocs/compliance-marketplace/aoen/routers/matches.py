from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Match, MatchStatus
from schemas import MatchOut
from services import matching_service, project_service, tenant_service

router = APIRouter()


@router.post("/{project_id}/run", response_model=list[MatchOut], status_code=status.HTTP_201_CREATED)
def run_matching(project_id: str, db: Session = Depends(get_db)):
    project = project_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    tenant = tenant_service.get_tenant(db, project.tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado.")

    return matching_service.run_project_matching(
        db=db,
        project=project,
        tenant_config_override=tenant.config or {},
        plan=tenant.plan or "starter",
    )


@router.get("/{project_id}", response_model=list[MatchOut])
def list_matches(project_id: str, db: Session = Depends(get_db)):
    project = project_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")
    return (
        db.query(Match)
        .filter(Match.project_id == project_id)
        .order_by(Match.score.desc())
        .all()
    )


@router.patch("/{match_id}/accept", response_model=MatchOut)
def accept_match(match_id: str, db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match não encontrado.")
    match.status = MatchStatus.ACCEPTED
    db.commit()
    db.refresh(match)
    return match


@router.patch("/{match_id}/reject", response_model=MatchOut)
def reject_match(match_id: str, db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match não encontrado.")
    match.status = MatchStatus.REJECTED
    db.commit()
    db.refresh(match)
    return match