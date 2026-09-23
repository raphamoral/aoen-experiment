from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from adapters.inbound.schemas.freelancer_schema import (
    FreelancerResponse,
    RateFreelancerRequest,
    RegisterFreelancerRequest,
    UpdateAvailabilityRequest,
)
from domain.exceptions import DomainException, FreelancerNotFound, ProjectNotFound
from domain.value_objects.compliance_area import ComplianceArea
from ports.inbound.freelancer_use_case import IFreelancerUseCase

router = APIRouter(prefix="/freelancers", tags=["Freelancers"])


def _serialize(freelancer) -> FreelancerResponse:
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


def get_use_case() -> IFreelancerUseCase:
    # Substituído no container via app.dependency_overrides
    raise NotImplementedError


FreelancerDep = Depends(get_use_case)


@router.post("/", response_model=FreelancerResponse, status_code=201)
def register_freelancer(
    body: RegisterFreelancerRequest,
    use_case: IFreelancerUseCase = FreelancerDep,
):
    try:
        return _serialize(
            use_case.register_freelancer(
                name=body.name,
                email=body.email,
                compliance_areas=body.compliance_areas,
                expertise_level=body.expertise_level,
                hourly_rate=body.hourly_rate,
                currency=body.currency,
                bio=body.bio,
                certifications=body.certifications,
            )
        )
    except DomainException as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/", response_model=List[FreelancerResponse])
def list_available_freelancers(
    area: Optional[ComplianceArea] = Query(None, description="Filtrar por área de compliance"),
    use_case: IFreelancerUseCase = FreelancerDep,
):
    return [_serialize(f) for f in use_case.list_available_freelancers(area=area)]


@router.get("/{freelancer_id}", response_model=FreelancerResponse)
def get_freelancer(
    freelancer_id: UUID,
    use_case: IFreelancerUseCase = FreelancerDep,
):
    try:
        return _serialize(use_case.get_freelancer(freelancer_id))
    except FreelancerNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{freelancer_id}/availability", response_model=FreelancerResponse)
def update_availability(
    freelancer_id: UUID,
    body: UpdateAvailabilityRequest,
    use_case: IFreelancerUseCase = FreelancerDep,
):
    try:
        return _serialize(use_case.update_availability(freelancer_id, body.available))
    except FreelancerNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{freelancer_id}/rating", response_model=FreelancerResponse)
def rate_freelancer(
    freelancer_id: UUID,
    body: RateFreelancerRequest,
    use_case: IFreelancerUseCase = FreelancerDep,
):
    try:
        return _serialize(use_case.rate_freelancer(freelancer_id, body.rating))
    except FreelancerNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (ValueError, DomainException) as e:
        raise HTTPException(status_code=422, detail=str(e))