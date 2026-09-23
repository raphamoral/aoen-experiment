from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from adapters.controllers.proposal_controller import (
    AcceptProposalRequest,
    ProposalController,
    SubmitProposalRequest,
)
from frameworks.http.dependencies import get_proposal_controller

router = APIRouter(prefix="/proposals", tags=["Proposals"])

ProposalDep = Annotated[ProposalController, Depends(get_proposal_controller)]


class SubmitProposalBody(BaseModel):
    project_id: str
    freelancer_id: str
    proposed_rate_amount: str
    cover_letter: str
    estimated_hours: int


class AcceptProposalBody(BaseModel):
    client_id: str


@router.post("/", status_code=status.HTTP_201_CREATED)
def submit_proposal(body: SubmitProposalBody, controller: ProposalDep) -> dict:
    try:
        return controller.submit(
            SubmitProposalRequest(
                project_id=body.project_id,
                freelancer_id=body.freelancer_id,
                proposed_rate_amount=body.proposed_rate_amount,
                cover_letter=body.cover_letter,
                estimated_hours=body.estimated_hours,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))


@router.post("/{proposal_id}/accept", status_code=status.HTTP_201_CREATED)
def accept_proposal(proposal_id: str, body: AcceptProposalBody, controller: ProposalDep) -> dict:
    try:
        return controller.accept(
            AcceptProposalRequest(proposal_id=proposal_id, client_id=body.client_id)
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))