from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from adapters.presenters.schemas import FreelancerCreateRequest, FreelancerResponse
from adapters.controllers.freelancer_controller import FreelancerController
from frameworks.web.dependencies import get_freelancer_controller

router = APIRouter(prefix="/freelancers", tags=["Freelancers"])


@router.post("/", response_model=FreelancerResponse, status_code=201)
def create_freelancer(
    request: FreelancerCreateRequest,
    controller: FreelancerController = Depends(get_freelancer_controller),
):
    try:
        return controller.create(request)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/", response_model=List[FreelancerResponse])
def list_freelancers(
    specialization: Optional[str] = Query(None, description="Filter by compliance area"),
    controller: FreelancerController = Depends(get_freelancer_controller),
):
    try:
        return controller.list_all(specialization)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/{freelancer_id}", response_model=FreelancerResponse)
def get_freelancer(
    freelancer_id: str,
    controller: FreelancerController = Depends(get_freelancer_controller),
):
    try:
        return controller.get(freelancer_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))