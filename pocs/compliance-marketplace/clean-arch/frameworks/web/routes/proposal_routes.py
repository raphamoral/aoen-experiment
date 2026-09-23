from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query

from adapters.presenters.schemas import (
    ProposalCreateRequest,
    ProposalAcceptRequest,
    ProposalResponse,
    ContractResponse,
)
from adapters.controllers.proposal_controller import ProposalController
from frameworks.web.dependencies import get_proposal_controller

router = APIRouter(prefix="/proposals", tags=["Proposals"])


@router.post("/", response_model=ProposalResponse, status_code=201)
def submit_proposal(
    request: ProposalCreateRequest,
    controller: ProposalController = Depends(get_proposal_controller),
):
    try:
        return controller.submit(request)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/{proposal_id}/accept", response_model=ContractResponse)
def accept_proposal(
    proposal_id: str,
    request: ProposalAcceptRequest,
    controller: ProposalController = Depends(get_proposal_controller),
):
    try:
        return controller.accept(proposal_id, request)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/by-project/{project_id}", response_model=List[ProposalResponse])
def list_proposals_by_project(
    project_id: str,
    client_id: str = Query(..., description="ID of the project owner"),
    controller: ProposalController = Depends(get_proposal_controller),
):
    try:
        return controller.list_by_project(project_id, client_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))