from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List

from ..application.services import MatchingService
from ..domain.value_objects import ProjectRequirement

router = APIRouter(prefix="/matching", tags=["Matching (Genesis)"])

_service = MatchingService()


class MatchRequest(BaseModel):
    client_id: str
    framework_codes: List[str]
    jurisdiction_codes: List[str]
    min_experience_years: int
    weekly_hours_needed: int
    complexity_level: int
    required_certifications: List[str] = []
    # Anti-Corruption Layer: em produção buscar via integração com contexto Freelancer
    freelancer_profiles: List[dict] = []


class MatchScoreResponse(BaseModel):
    value: float
    framework_alignment: float
    jurisdiction_match: float
    seniority_fit: float
    availability_fit: float
    certification_bonus: float


class MatchResultResponse(BaseModel):
    match_id: str
    freelancer_id: str
    score: MatchScoreResponse
    status: str


@router.post("/", response_model=List[MatchResultResponse])
async def find_matches(request: MatchRequest):
    """
    Executa o algoritmo de matching compliance-especializado.

    Retorna freelancers ranqueados por compatibilidade com os requisitos
    regulatórios do projeto. Score ≥ 0.30 para aparecer nos resultados.
    """
    requirement = ProjectRequirement(
        framework_codes=tuple(request.framework_codes),
        jurisdiction_codes=tuple(request.jurisdiction_codes),
        min_experience_years=request.min_experience_years,
        weekly_hours_needed=request.weekly_hours_needed,
        complexity_level=request.complexity_level,
        required_certifications=tuple(request.required_certifications),
    )
    results = await _service.find_matches(
        client_id=request.client_id,
        requirement=requirement,
        freelancer_profiles=request.freelancer_profiles,
    )
    return [
        MatchResultResponse(
            match_id=r.id,
            freelancer_id=r.freelancer_id,
            score=MatchScoreResponse(
                value=r.score.value,
                framework_alignment=r.score.framework_alignment,
                jurisdiction_match=r.score.jurisdiction_match,
                seniority_fit=r.score.seniority_fit,
                availability_fit=r.score.availability_fit,
                certification_bonus=r.score.certification_bonus,
            ),
            status=r.status.value,
        )
        for r in results
    ]


@router.patch("/{match_id}/accept")
async def accept_match(match_id: str):
    """Cliente aceita o match — inicia fluxo de contratação."""
    try:
        match = await _service.accept_match(match_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return {"match_id": match.id, "status": match.status.value}


@router.patch("/{match_id}/reject")
async def reject_match(match_id: str):
    """Cliente rejeita o match — descarta sugestão."""
    try:
        match = await _service.reject_match(match_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return {"match_id": match.id, "status": match.status.value}