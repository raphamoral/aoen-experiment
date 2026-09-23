from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from shared.infra.database import get_db
from contexts.nutrition.application.services import NutritionalPlanService
from contexts.nutrition.domain.value_objects import MealDistribution
from contexts.nutrition.infrastructure.repository import NutritionalPlanRepository

router = APIRouter(prefix="/nutrition", tags=["Planos Nutricionais"])


class GeneratePlanInput(BaseModel):
    user_id: UUID
    lab_result_id: UUID
    meal_distribution: str = "balanceada"
    altered_biomarkers: List[dict] = []


class DailyTargetOutput(BaseModel):
    nutrient_name: str
    target_amount: float
    unit: str
    category: str
    priority: str


class NutritionalPlanOutput(BaseModel):
    id: str
    user_id: str
    lab_result_id: str
    meal_distribution: str
    daily_targets: List[DailyTargetOutput]
    clinical_notes: str
    is_active: bool
    high_priority_count: int


def get_service(db: Session = Depends(get_db)) -> NutritionalPlanService:
    return NutritionalPlanService(NutritionalPlanRepository(db))


@router.post("/plans", response_model=NutritionalPlanOutput, status_code=201)
async def generate_nutritional_plan(
    payload: GeneratePlanInput,
    service: NutritionalPlanService = Depends(get_service),
):
    """Gera Plano Nutricional Personalizado.

    Traduz biomarcadores alterados em metas de ingestão diária,
    aplicando correlações clínicas nutrição-laboratório.
    """
    try:
        dist = MealDistribution(payload.meal_distribution)
    except ValueError:
        dist = MealDistribution.BALANCED

    plan = await service.generate_from_lab_result(
        user_id=payload.user_id,
        lab_result_id=payload.lab_result_id,
        altered_biomarkers=payload.altered_biomarkers,
        meal_distribution=dist,
    )
    return _to_output(plan)


@router.get("/plans/user/{user_id}/active", response_model=NutritionalPlanOutput)
def get_active_plan(
    user_id: UUID,
    service: NutritionalPlanService = Depends(get_service),
):
    plan = service.get_active_plan(user_id)
    if not plan:
        raise HTTPException(
            status_code=404, detail="Nenhum plano nutricional ativo encontrado"
        )
    return _to_output(plan)


@router.get("/plans/user/{user_id}", response_model=List[NutritionalPlanOutput])
def list_user_plans(
    user_id: UUID,
    service: NutritionalPlanService = Depends(get_service),
):
    return [_to_output(p) for p in service.list_by_user(user_id)]


def _to_output(plan) -> NutritionalPlanOutput:
    return NutritionalPlanOutput(
        id=str(plan.id),
        user_id=str(plan.user_id),
        lab_result_id=str(plan.lab_result_id),
        meal_distribution=plan.meal_distribution.value,
        daily_targets=[
            DailyTargetOutput(
                nutrient_name=t.nutrient_name,
                target_amount=t.target_amount,
                unit=t.unit,
                category=t.category.value,
                priority=t.priority,
            )
            for t in plan.daily_targets
        ],
        clinical_notes=plan.clinical_notes,
        is_active=plan.is_active,
        high_priority_count=len(plan.high_priority_nutrients),
    )