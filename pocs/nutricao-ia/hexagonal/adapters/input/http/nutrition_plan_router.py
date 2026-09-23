from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from adapters.input.http.schemas import (
    DietaryRecommendationResponse,
    GenerateNutritionPlanRequest,
    NutritionPlanResponse,
)
from domain.exceptions import (
    DomainValidationError,
    LabExamNotFoundError,
    NutritionPlanNotFoundError,
    PatientNotFoundError,
)
from ports.input.generate_nutrition_plan_use_case import (
    GenerateNutritionPlanCommand,
    GenerateNutritionPlanUseCasePort,
)
from ports.input.get_nutrition_plan_use_case import GetNutritionPlanUseCasePort
from config.dependencies import (
    get_generate_nutrition_plan_use_case,
    get_nutrition_plan_use_case,
)

router = APIRouter(prefix="/nutrition-plans", tags=["nutrition-plans"])


def _plan_to_response(plan) -> NutritionPlanResponse:
    return NutritionPlanResponse(
        id=plan.id,
        patient_id=plan.patient_id,
        lab_exam_id=plan.lab_exam_id,
        recommendations=[
            DietaryRecommendationResponse(
                nutrient=r.nutrient,
                level=r.level.value,
                foods_to_increase=r.foods_to_increase,
                foods_to_avoid=r.foods_to_avoid,
                supplements=r.supplements,
                clinical_notes=r.clinical_notes,
            )
            for r in plan.recommendations
        ],
        general_notes=plan.general_notes,
        ai_analysis=plan.ai_analysis,
        has_critical_deficiencies=plan.has_critical_deficiencies,
        abnormal_nutrients=plan.abnormal_nutrients,
        created_at=plan.created_at,
    )


@router.post(
    "/generate",
    response_model=NutritionPlanResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_nutrition_plan(
    body: GenerateNutritionPlanRequest,
    use_case: GenerateNutritionPlanUseCasePort = Depends(
        get_generate_nutrition_plan_use_case
    ),
) -> NutritionPlanResponse:
    try:
        plan = await use_case.execute(
            GenerateNutritionPlanCommand(
                patient_id=body.patient_id,
                lab_exam_id=body.lab_exam_id,
            )
        )
    except PatientNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except LabExamNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except DomainValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    return _plan_to_response(plan)


@router.get("/{plan_id}", response_model=NutritionPlanResponse)
async def get_nutrition_plan(
    plan_id: UUID,
    use_case: GetNutritionPlanUseCasePort = Depends(get_nutrition_plan_use_case),
) -> NutritionPlanResponse:
    plan = await use_case.get_by_id(plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nutrition plan not found: {plan_id}",
        )
    return _plan_to_response(plan)


@router.get("/patient/{patient_id}", response_model=list[NutritionPlanResponse])
async def get_patient_plans(
    patient_id: UUID,
    use_case: GetNutritionPlanUseCasePort = Depends(get_nutrition_plan_use_case),
) -> list[NutritionPlanResponse]:
    plans = await use_case.get_by_patient(patient_id)
    return [_plan_to_response(p) for p in plans]