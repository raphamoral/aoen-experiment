from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from adapters.inbound.schemas.proposal_schema import ProposalResponse, SubmitProposalRequest
from domain.exceptions import (
    DomainException,
    FreelancerNotFound,
    IncompatibleExpertise,
    ProjectNotFound,
    ProposalNotFound,
)
from ports.inbound.proposal_use_case import IProposalUseCase

router = APIRouter(prefix="/proposals", tags=["Propostas"])


def _serialize(proposal) -> ProposalResponse:
    return ProposalResponse(
        id=proposal.id,
        project_id=proposal.project_id,
        freelancer_id=proposal.freelancer_id,
        proposed_rate=proposal.proposed_rate,
        cover_letter=proposal.cover_letter,
        estimated_hours=proposal.estimated_hours,
        total_cost=proposal.total_cost,
        status=proposal.status,
    )


def get_use_case() -> IProposalUseCase:
    raise NotImplementedError


ProposalDep = Depends(get_use_case)


@router.post("/", response_model=ProposalResponse, status_code=201)
def submit_proposal(
    body: SubmitProposalRequest,
    use_case: IProposalUseCase = ProposalDep,
):
    try:
        return _serialize(
            use_case.submit_proposal(
                project_id=body.project_id,
                freelancer_id=body.freelancer_id,
                proposed_rate=body.proposed_rate,
                cover_letter=body.cover_letter,
                estimated_hours=body.estimated_hours,
            )
        )
    except (ProjectNotFound, FreelancerNotFound) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except IncompatibleExpertise as e:
        raise HTTPException(status_code=409, detail=str(e))
    except DomainException as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/project/{project_id}", response_model=List[ProposalResponse])
def list_proposals_for_project(
    project_id: UUID,
    use_case: IProposalUseCase = ProposalDep,
):
    return [_serialize(p) for p in use_case.list_proposals_for_project(project_id)]


@router.get("/freelancer/{freelancer_id}", response_model=List[ProposalResponse])
def list_proposals_by_freelancer(
    freelancer_id: UUID,
    use_case: IProposalUseCase = ProposalDep,
):
    return [_serialize(p) for p in use_case.list_proposals_by_freelancer(freelancer_id)]


@router.post("/{proposal_id}/accept", response_model=ProposalResponse)
def accept_proposal(proposal_id: UUID, use_case: IProposalUseCase = ProposalDep):
    try:
        return _serialize(use_case.accept_proposal(proposal_id))
    except ProposalNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DomainException as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/{proposal_id}/reject", response_model=ProposalResponse)
def reject_proposal(proposal_id: UUID, use_case: IProposalUseCase = ProposalDep):
    try:
        return _serialize(use_case.reject_proposal(proposal_id))
    except ProposalNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DomainException as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/{proposal_id}/withdraw", response_model=ProposalResponse)
def withdraw_proposal(proposal_id: UUID, use_case: IProposalUseCase = ProposalDep):
    try:
        return _serialize(use_case.withdraw_proposal(proposal_id))
    except ProposalNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DomainException as e:
        raise HTTPException(status_code=422, detail=str(e))