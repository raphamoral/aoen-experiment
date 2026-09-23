from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.schemas import ProposalCreate, ProposalResponse
from src.infrastructure.database import get_db
from src.infrastructure.repositories import (
    AuditRepository,
    FreelancerRepository,
    ProjectRepository,
    ProposalRepository,
)
from src.services.proposal_service import ProposalService

router = APIRouter()


def _service(db: AsyncSession = Depends(get_db)) -> ProposalService:
    return ProposalService(
        proposal_repo=ProposalRepository(db),
        project_repo=ProjectRepository(db),
        freelancer_repo=FreelancerRepository(db),
        audit=AuditRepository(db),
    )


@router.post("", response_model=ProposalResponse, status_code=status.HTTP_201_CREATED)
async def submit_proposal(
    body: ProposalCreate,
    svc: ProposalService = Depends(_service),
):
    try:
        proposal = await svc.submit_proposal(
            project_id=body.project_id,
            freelancer_id=body.freelancer_id,
            cover_letter=body.cover_letter,
            proposed_rate_brl=body.proposed_rate_brl,
            estimated_hours=body.estimated_hours,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return ProposalResponse(
        id=proposal.id,
        project_id=proposal.project_id,
        freelancer_id=proposal.freelancer_id,
        cover_letter=proposal.cover_letter,
        proposed_rate_brl=proposal.proposed_rate_brl,
        estimated_hours=proposal.estimated_hours,
        total_cost_brl=proposal.total_cost_brl,
        status=proposal.status,
        submitted_at=proposal.submitted_at,
    )


@router.post("/{proposal_id}/accept", response_model=ProposalResponse)
async def accept_proposal(
    proposal_id: str,
    actor_id: UUID,
    svc: ProposalService = Depends(_service),
):
    try:
        pid = UUID(proposal_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID inválido")
    try:
        proposal = await svc.accept_proposal(pid, actor_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return ProposalResponse(
        id=proposal.id,
        project_id=proposal.project_id,
        freelancer_id=proposal.freelancer_id,
        cover_letter=proposal.cover_letter,
        proposed_rate_brl=proposal.proposed_rate_brl,
        estimated_hours=proposal.estimated_hours,
        total_cost_brl=proposal.total_cost_brl,
        status=proposal.status,
        submitted_at=proposal.submitted_at,
    )


@router.get("/project/{project_id}", response_model=List[ProposalResponse])
async def list_proposals_for_project(
    project_id: str,
    svc: ProposalService = Depends(_service),
):
    try:
        pid = UUID(project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID inválido")
    proposals = await svc.list_for_project(pid)
    return [
        ProposalResponse(
            id=p.id,
            project_id=p.project_id,
            freelancer_id=p.freelancer_id,
            cover_letter=p.cover_letter,
            proposed_rate_brl=p.proposed_rate_brl,
            estimated_hours=p.estimated_hours,
            total_cost_brl=p.total_cost_brl,
            status=p.status,
            submitted_at=p.submitted_at,
        )
        for p in proposals
    ]