from typing import List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.schemas import FreelancerCreate, FreelancerResponse
from src.domain.models import ComplianceArea
from src.infrastructure.database import get_db
from src.infrastructure.repositories import AuditRepository, FreelancerRepository
from src.services.freelancer_service import FreelancerService

router = APIRouter()


def _service(db: AsyncSession = Depends(get_db)) -> FreelancerService:
    return FreelancerService(
        repo=FreelancerRepository(db),
        audit=AuditRepository(db),
    )


@router.post("", response_model=FreelancerResponse, status_code=status.HTTP_201_CREATED)
async def register_freelancer(
    body: FreelancerCreate,
    svc: FreelancerService = Depends(_service),
):
    freelancer = await svc.register(
        name=body.name,
        email=body.email,
        bio=body.bio,
        areas=body.areas,
        hourly_rate_brl=body.hourly_rate_brl,
        actor_id=uuid4(),
    )
    return FreelancerResponse(
        id=freelancer.id,
        name=freelancer.name,
        email=freelancer.email,
        bio=freelancer.bio,
        areas=freelancer.areas,
        hourly_rate_brl=freelancer.hourly_rate_brl,
        reputation_score=freelancer.reputation_score,
        created_at=freelancer.created_at,
    )


@router.get("", response_model=List[FreelancerResponse])
async def list_freelancers(
    area: ComplianceArea | None = None,
    svc: FreelancerService = Depends(_service),
):
    if area:
        freelancers = await svc.find_by_area(area)
    else:
        freelancers = await svc.list_all()
    return [
        FreelancerResponse(
            id=f.id,
            name=f.name,
            email=f.email,
            bio=f.bio,
            areas=f.areas,
            hourly_rate_brl=f.hourly_rate_brl,
            reputation_score=f.reputation_score,
            created_at=f.created_at,
        )
        for f in freelancers
    ]


@router.get("/{freelancer_id}", response_model=FreelancerResponse)
async def get_freelancer(
    freelancer_id: str,
    svc: FreelancerService = Depends(_service),
):
    from uuid import UUID
    try:
        fid = UUID(freelancer_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID inválido")

    freelancer = await svc.get(fid)
    if not freelancer:
        raise HTTPException(status_code=404, detail="Freelancer não encontrado")
    return FreelancerResponse(
        id=freelancer.id,
        name=freelancer.name,
        email=freelancer.email,
        bio=freelancer.bio,
        areas=freelancer.areas,
        hourly_rate_brl=freelancer.hourly_rate_brl,
        reputation_score=freelancer.reputation_score,
        created_at=freelancer.created_at,
    )