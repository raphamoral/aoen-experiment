import os
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from shared.infra.database import get_db
from contexts.ai_analysis.application.services import AIAnalysisOrchestrator
from contexts.ai_analysis.infrastructure.llm_gateway import AnthropicLLMGateway
from contexts.ai_analysis.infrastructure.repository import AnalysisRepository

router = APIRouter(prefix="/analysis", tags=["Análise por IA"])


class BiomarkerContext(BaseModel):
    name: str
    value: float
    unit: str
    status: str
    ref_min: Optional[float] = None
    ref_max: Optional[float] = None


class UserContext(BaseModel):
    age: Optional[int] = None
    biological_sex: Optional[str] = None
    health_goals: List[str] = []
    health_conditions: List[str] = []


class AnalysisRequest(BaseModel):
    user_id: UUID
    lab_result_id: UUID
    biomarkers: List[BiomarkerContext]
    user_context: Optional[UserContext] = None


class InsightOutput(BaseModel):
    title: str
    description: str
    risk_level: str
    category: str
    biomarkers_involved: List[str]
    recommendation: str
    evidence_basis: str
    is_actionable: bool


class AnalysisOutput(BaseModel):
    id: str
    user_id: str
    lab_result_id: str
    summary: str
    insights: List[InsightOutput]
    model_used: str
    critical_count: int
    actionable_count: int


def get_service(db: Session = Depends(get_db)) -> AIAnalysisOrchestrator:
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="Serviço de IA não configurado: defina ANTHROPIC_API_KEY",
        )
    return AIAnalysisOrchestrator(
        repository=AnalysisRepository(db),
        llm_gateway=AnthropicLLMGateway(api_key=api_key),
    )


@router.post("/generate", response_model=AnalysisOutput, status_code=201)
async def generate_analysis(
    payload: AnalysisRequest,
    service: AIAnalysisOrchestrator = Depends(get_service),
):
    """Gera Análise Personalizada por IA.

    Envia biomarcadores ao Claude (Anthropic) que identifica correlações
    clínicas e gera insights nutricionais acionáveis.

    Core capability — Genesis no Wardley Map: diferencial central do produto.
    """
    analysis = await service.generate_analysis(
        user_id=payload.user_id,
        lab_result_id=payload.lab_result_id,
        biomarkers=[b.model_dump() for b in payload.biomarkers],
        user_context=(
            payload.user_context.model_dump() if payload.user_context else None
        ),
    )
    return _to_output(analysis)


@router.get("/{analysis_id}", response_model=AnalysisOutput)
def get_analysis(
    analysis_id: UUID,
    service: AIAnalysisOrchestrator = Depends(get_service),
):
    analysis = service.get_by_id(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Análise não encontrada")
    return _to_output(analysis)


@router.get("/lab-result/{lab_result_id}", response_model=AnalysisOutput)
def get_analysis_by_lab_result(
    lab_result_id: UUID,
    service: AIAnalysisOrchestrator = Depends(get_service),
):
    analysis = service.get_by_lab_result(lab_result_id)
    if not analysis:
        raise HTTPException(
            status_code=404, detail="Análise não encontrada para este exame"
        )
    return _to_output(analysis)


def _to_output(analysis) -> AnalysisOutput:
    return AnalysisOutput(
        id=str(analysis.id),
        user_id=str(analysis.user_id),
        lab_result_id=str(analysis.lab_result_id),
        summary=analysis.summary,
        insights=[
            InsightOutput(
                title=i.title,
                description=i.description,
                risk_level=i.risk_level.value,
                category=i.category.value,
                biomarkers_involved=i.biomarkers_involved,
                recommendation=i.recommendation,
                evidence_basis=i.evidence_basis,
                is_actionable=i.is_actionable(),
            )
            for i in analysis.insights
        ],
        model_used=analysis.model_used,
        critical_count=len(analysis.critical_insights),
        actionable_count=len(analysis.actionable_insights),
    )