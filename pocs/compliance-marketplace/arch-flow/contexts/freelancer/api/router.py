from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

from ..application.commands import (
    AddCertificationCommand,
    AddSpecializationCommand,
    ApproveFreelancerCommand,
    RegisterFreelancerCommand,
)
from ..application.services import FreelancerService
from ..infrastructure.repository import FreelancerRepository

router = APIRouter(prefix="/freelancers", tags=["Freelancer (Custom)"])

_repository = FreelancerRepository()
_service = FreelancerService(_repository)


class RegisterFreelancerRequest(BaseModel):
    user_id: str
    full_name: str
    headline: str
    bio: str
    hourly_rate_brl: float
    years_of_experience: int
    availability_hours_per_week: int
    max_complexity_level: int = 1


class AddSpecializationRequest(BaseModel):
    specialization_code: str
    specialization_description: str
    regulatory_body: str


class AddCertificationRequest(BaseModel):
    name: str
    issuer: str
    valid_until: str
    credential_url: str = ""


class FreelancerResponse(BaseModel):
    id: str
    full_name: str
    headline: str
    status: str
    hourly_rate_brl: Optional[float]
    years_of_experience: int
    availability_hours_per_week: int
    max_complexity_level: int
    specializations: List[dict]
    certifications: List[dict]


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=FreelancerResponse)
async def register_freelancer(request: RegisterFreelancerRequest):
    """Registra novo freelancer especializado em compliance regulatório."""
    cmd = RegisterFreelancerCommand(**request.model_dump())
    profile = await _service.register_freelancer(cmd)
    return _to_response(profile)


@router.patch("/{freelancer_id}/approve")
async def approve_freelancer(freelancer_id: str, reviewer_id: str):
    """Aprovação editorial — torna o perfil visível para matching com clientes."""
    cmd = ApproveFreelancerCommand(
        freelancer_id=freelancer_id, reviewer_id=reviewer_id
    )
    profile = await _service.approve_freelancer(cmd)
    return _to_response(profile)


@router.post("/{freelancer_id}/specializations")
async def add_specialization(freelancer_id: str, request: AddSpecializationRequest):
    """Adiciona especialização regulatória (LGPD, BACEN, CVM...) ao perfil."""
    cmd = AddSpecializationCommand(
        freelancer_id=freelancer_id, **request.model_dump()
    )
    profile = await _service.add_specialization(cmd)
    return _to_response(profile)


@router.post("/{freelancer_id}/certifications")
async def add_certification(freelancer_id: str, request: AddCertificationRequest):
    """Registra certificação profissional (CCEP, CISA, CFE...) ao perfil."""
    cmd = AddCertificationCommand(
        freelancer_id=freelancer_id, **request.model_dump()
    )
    profile = await _service.add_certification(cmd)
    return _to_response(profile)


@router.get("/{freelancer_id}", response_model=FreelancerResponse)
async def get_freelancer(freelancer_id: str):
    profile = await _service.find_by_id(freelancer_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Freelancer não encontrado"
        )
    return _to_response(profile)


@router.get("/", response_model=List[FreelancerResponse])
async def list_active_freelancers():
    """Lista freelancers ativos disponíveis para contratação."""
    profiles = await _service.find_active_freelancers()
    return [_to_response(p) for p in profiles]


def _to_response(profile) -> dict:
    return {
        "id": profile.id,
        "full_name": profile.full_name,
        "headline": profile.headline,
        "status": profile.status.value,
        "hourly_rate_brl": profile.hourly_rate.amount if profile.hourly_rate else None,
        "years_of_experience": profile.years_of_experience,
        "availability_hours_per_week": profile.availability_hours_per_week,
        "max_complexity_level": profile.max_complexity_level,
        "specializations": [
            {
                "code": s.code,
                "description": s.description,
                "regulatory_body": s.regulatory_body,
            }
            for s in profile.specializations
        ],
        "certifications": [
            {"name": c.name, "issuer": c.issuer, "valid_until": c.valid_until}
            for c in profile.certifications
        ],
    }