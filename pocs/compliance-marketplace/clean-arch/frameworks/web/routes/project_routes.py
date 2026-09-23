from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from adapters.presenters.schemas import ProjectCreateRequest, ProjectResponse
from adapters.controllers.project_controller import ProjectController
from frameworks.web.dependencies import get_project_controller

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/", response_model=ProjectResponse, status_code=201)
def post_project(
    request: ProjectCreateRequest,
    controller: ProjectController = Depends(get_project_controller),
):
    try:
        return controller.post(request)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/", response_model=List[ProjectResponse])
def list_projects(
    compliance_area: Optional[str] = Query(None, description="Filter by compliance area"),
    status: Optional[str] = Query(None, description="OPEN | IN_PROGRESS | COMPLETED | CANCELLED"),
    controller: ProjectController = Depends(get_project_controller),
):
    try:
        return controller.list_open(compliance_area, status)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))