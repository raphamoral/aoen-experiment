from fastapi import APIRouter, Depends, HTTPException

from adapters.controllers.nutrition_controller import NutritionController
from frameworks.api.schemas.nutrition_schema import GeneratePlanSchema
from frameworks.container import get_nutrition_controller

router = APIRouter(prefix="/patients/{patient_id}/nutrition-plans", tags=["nutrition"])


@router.post("/", status_code=201)
def generate_nutrition_plan(
    patient_id: str,
    body: GeneratePlanSchema,
    controller: NutritionController = Depends(get_nutrition_controller),
):
    try:
        return controller.generate_plan(patient_id, body.exam_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))