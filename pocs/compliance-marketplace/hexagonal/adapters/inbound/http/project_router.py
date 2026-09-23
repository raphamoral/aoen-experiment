from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from adapters.inbound.schemas.freelancer_schema import FreelancerResponse
from adapters.inbound.schemas.project_schema import CreateProjectRequest, ProjectResponse
from domain.exceptions import DomainException, ProjectNotFound
from ports.inbound.freelancer_use_case import IFreelancerUseCase
from ports.inbound.project_use_case import IProjectUseCase

router = APIRouter(prefix="/projects", tags=["Projetos"])


def _serialize_project(project) -> ProjectResponse:
    return ProjectResponse(
        id=project.id,
        title=project.title,
        description=project.description,
        client_id=project.client_id,
        required_areas=project.required_areas,
        budget=project.budget,
        deadline=project.deadline,
        status=project.status,
        assigned_freelancer_id=project.assigned_freelancer_id,
    )


def _serialize_freelancer(freelancer) -> FreelancerResponse:
    return FreelancerResponse(
        id=freelancer.id,
        name=freelancer.name,
        email=freelancer.email,
        compliance_areas=freelancer.compliance_areas,
        expertise_level=freelancer.expertise_level,
        hourly_rate=freelancer.hourly_rate.amount,
        currency=freelancer.hourly_rate.currency,
        bio=freelancer.bio,
        certifications=freelancer.certifications,
        is_available=freelancer.is_available,
        rating=freelancer.rating,
    )


def get_project_use_case() -> IProjectUseCase:
    raise NotImplementedError


def get_freelancer_use_case() -> IFreelancerUseCase:
    raise NotImplementedError


ProjectDep = Depends(get_project_use_case)
FreelancerDep = Depends(get_freelancer_use_case)


@router.post("/", response_model=ProjectResponse, status_code=201)
def create_project(
    body: CreateProjectRequest,
    use_case: IProjectUseCase = ProjectDep,
):
    try:
        return _serialize_project(
            use_case.create_project(
                title=body.title,
                description=body.description,
                client_id=body.client_id,
                required_areas=body.required_areas,
                budget=body.budget,
                deadline=body.deadline,
            )
        )
    except DomainException as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/", response_model=List[ProjectResponse])
def list_open_projects(use_case: IProjectUseCase = ProjectDep):
    return [_serialize_project(p) for p in use_case.list_open_projects()]


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: UUID, use_case: IProjectUseCase = ProjectDep):
    try:
        return _serialize_project(use_case.get_project(project_id))
    except ProjectNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{project_id}/cancel", response_model=ProjectResponse)
def cancel_project(project_id: UUID, use_case: IProjectUseCase = ProjectDep):
    try:
        return _serialize_project(use_case.cancel_project(project_id))
    except ProjectNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DomainException as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/{project_id}/complete", response_model=ProjectResponse)
def complete_project(project_id: UUID, use_case: IProjectUseCase = ProjectDep):
    try:
        return _serialize_project(use_case.complete_project(project_id))
    except ProjectNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DomainException as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/{project_id}/candidates", response_model=List[FreelancerResponse])
def find_candidates(
    project_id: UUID,
    project_use_case: IProjectUseCase = ProjectDep,
    freelancer_use_case: IFreelancerUseCase = FreelancerDep,
):
    """Retorna freelancers elegíveis ordenados por rating e menor taxa horária."""
    try:
        return [
            _serialize_freelancer(f)
            for f in freelancer_use_case.find_candidates_for_project(project_id)
        ]
    except ProjectNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))