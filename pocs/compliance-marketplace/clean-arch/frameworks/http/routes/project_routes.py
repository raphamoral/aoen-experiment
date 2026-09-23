from datetime import datetime
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from adapters.controllers.project_controller import CreateProjectRequest, ProjectController
from frameworks.http.dependencies import get_project_controller

router = APIRouter(prefix="/projects", tags=["Projects"])

ProjectDep = Annotated[ProjectController, Depends(get_project_controller)]


class CreateProjectBody(BaseModel):
    client_id: str
    title: str
    description: str
    required_specialties: List[str]
    budget_amount: str
    deadline: datetime


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_project(body: CreateProjectBody, controller: ProjectDep) -> dict:
    try:
        return controller.create(
            CreateProjectRequest(
                client_id=body.client_id,
                title=body.title,
                description=body.description,
                required_specialties=body.required_specialties,
                budget_amount=body.budget_amount,
                deadline=body.deadline,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))


@router.get("/open")
def list_open_projects(
    controller: ProjectDep,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> dict:
    return controller.list_open(skip=skip, limit=limit)