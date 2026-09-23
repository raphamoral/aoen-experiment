from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from services.ai_service import AIService
from services.nutrition_service import NutritionService

router = APIRouter()


class GeneratePlanRequest(BaseModel):
    patient_id: str
    analysis_id: str


@router.post("/generate", status_code=201)
async def generate_nutrition_plan(
    body: GeneratePlanRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Gera plano nutricional combinando:
    - core/nutrition_engine.py (regras baseadas em evidências, sem IA)
    - AIService (narrativa humanizada via Claude — modelo configurável por tenant)
    """
    tenant_id = request.state.tenant_id
    service = NutritionService(db, AIService())
    try:
        plan = await service.generate_nutrition_plan(
            patient_id=body.patient_id,
            analysis_id=body.analysis_id,
            tenant_id=tenant_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return {
        "plan_id": plan.id,
        "patient_id": plan.patient_id,
        "analysis_id": plan.analysis_id,
        "status": plan.status.value,
        "valid_until": plan.valid_until,
        "ai_model_used": plan.ai_model_used,
        "created_at": plan.created_at.isoformat(),
    }


@router.get("/patient/{patient_id}")
async def list_patient_plans(
    patient_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    tenant_id = request.state.tenant_id
    service = NutritionService(db, AIService())
    plans = await service.get_patient_plans(patient_id, tenant_id)
    return [
        {
            "plan_id": p.id,
            "analysis_id": p.analysis_id,
            "status": p.status.value,
            "valid_until": p.valid_until,
            "ai_model_used": p.ai_model_used,
            "created_at": p.created_at.isoformat(),
        }
        for p in plans
    ]


@router.get("/{plan_id}")
async def get_plan(
    plan_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    tenant_id = request.state.tenant_id
    service = NutritionService(db, AIService())
    plan = await service.get_plan_by_id(plan_id, tenant_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    return {
        "plan_id": plan.id,
        "patient_id": plan.patient_id,
        "analysis_id": plan.analysis_id,
        "ai_narrative": plan.ai_narrative,
        "ai_model_used": plan.ai_model_used,
        "status": plan.status.value,
        "valid_until": plan.valid_until,
        "recommendations": [
            {
                "id": r.id,
                "category": r.category.value,
                "priority": r.priority,
                "target_biomarker": r.target_biomarker,
                "recommendation": r.recommendation,
                "rationale": r.rationale,
            }
            for r in plan.recommendations
        ],
        "created_at": plan.created_at.isoformat(),
    }