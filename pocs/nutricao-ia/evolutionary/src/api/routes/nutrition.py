from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.api.dependencies import get_nutrition_service

router = APIRouter()


class GeneratePlanRequest(BaseModel):
    user_id: int
    exam_panel_id: int | None = None


@router.post("/generate")
async def generate_nutrition_plan(
    payload: GeneratePlanRequest, service=Depends(get_nutrition_service)
):
    result = await service.generate_plan(
        user_id=payload.user_id,
        exam_panel_id=payload.exam_panel_id,
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/user/{user_id}")
async def list_user_plans(user_id: int, service=Depends(get_nutrition_service)):
    plans = await service.list_user_plans(user_id)
    return [
        {
            "id": p.id,
            "created_at": p.created_at.isoformat(),
            "meta_calorica": p.daily_calories,
            "version": p.version,
            "ai_provider_used": p.ai_provider_used,
        }
        for p in plans
    ]


@router.get("/{plan_id}")
async def get_nutrition_plan(plan_id: int, service=Depends(get_nutrition_service)):
    plan = await service.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plano nutricional não encontrado")
    return {
        "id": plan.id,
        "user_id": plan.user_id,
        "deficiencias": plan.deficiencies,
        "recomendacoes": plan.recommendations,
        "restricoes": plan.restrictions,
        "suplementos": plan.supplements,
        "meta_calorica": plan.daily_calories,
        "macros": plan.macros,
        "ai_provider_used": plan.ai_provider_used,
        "created_at": plan.created_at.isoformat(),
    }