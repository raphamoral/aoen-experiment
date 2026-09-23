import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_freelancer
from app.models import Freelancer
from app.schemas import FreelancerCreate, FreelancerResponse, FreelancerUpdate

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _parse_list(value: str | None) -> list[str]:
    return [v.strip() for v in value.split(",")] if value else []


def _serialize_list(values: list[str]) -> str:
    return ",".join(values)


@router.post("", response_model=FreelancerResponse, status_code=status.HTTP_201_CREATED)
async def register_freelancer(
    payload: FreelancerCreate,
    db: AsyncSession = Depends(get_db),
) -> FreelancerResponse:
    existing = await db.execute(select(Freelancer).where(Freelancer.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email já cadastrado")

    freelancer = Freelancer(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=pwd_context.hash(payload.password),
        bio=payload.bio,
        hourly_rate=payload.hourly_rate,
        domains=_serialize_list([d.value for d in payload.domains]),
        certifications=_serialize_list(payload.certifications),
    )
    db.add(freelancer)
    await db.flush()
    await db.refresh(freelancer)
    return _to_response(freelancer)


@router.get("", response_model=list[FreelancerResponse])
async def list_freelancers(
    domain: str | None = Query(default=None, description="Filtrar por domínio de compliance"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> list[FreelancerResponse]:
    query = select(Freelancer).where(Freelancer.is_active == True).offset(skip).limit(limit)
    if domain:
        query = query.where(Freelancer.domains.contains(domain))
    result = await db.execute(query)
    return [_to_response(f) for f in result.scalars().all()]


@router.get("/me", response_model=FreelancerResponse)
async def get_me(current: Freelancer = Depends(get_current_freelancer)) -> FreelancerResponse:
    return _to_response(current)


@router.get("/{freelancer_id}", response_model=FreelancerResponse)
async def get_freelancer(freelancer_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> FreelancerResponse:
    result = await db.execute(select(Freelancer).where(Freelancer.id == freelancer_id))
    freelancer = result.scalar_one_or_none()
    if not freelancer:
        raise HTTPException(status_code=404, detail="Freelancer não encontrado")
    return _to_response(freelancer)


@router.patch("/me", response_model=FreelancerResponse)
async def update_me(
    payload: FreelancerUpdate,
    current: Freelancer = Depends(get_current_freelancer),
    db: AsyncSession = Depends(get_db),
) -> FreelancerResponse:
    if payload.bio is not None:
        current.bio = payload.bio
    if payload.hourly_rate is not None:
        current.hourly_rate = payload.hourly_rate
    if payload.domains is not None:
        current.domains = _serialize_list([d.value for d in payload.domains])
    if payload.certifications is not None:
        current.certifications = _serialize_list(payload.certifications)
    await db.flush()
    await db.refresh(current)
    return _to_response(current)


def _to_response(f: Freelancer) -> FreelancerResponse:
    return FreelancerResponse(
        id=f.id,
        email=f.email,
        full_name=f.full_name,
        bio=f.bio,
        hourly_rate=float(f.hourly_rate) if f.hourly_rate else None,
        domains=_parse_list(f.domains),
        certifications=_parse_list(f.certifications),
        is_active=f.is_active,
        created_at=f.created_at,
    )