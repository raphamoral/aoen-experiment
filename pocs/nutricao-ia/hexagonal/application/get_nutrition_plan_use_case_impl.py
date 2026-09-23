from uuid import UUID

from domain.entities.nutrition_plan import NutritionPlan
from ports.input.get_nutrition_plan_use_case import GetNutritionPlanUseCasePort
from ports.output.nutrition_plan_repository_port import NutritionPlanRepositoryPort


class GetNutritionPlanUseCaseImpl(GetNutritionPlanUseCasePort):
    def __init__(self, nutrition_plan_repo: NutritionPlanRepositoryPort) -> None:
        self._nutrition_plan_repo = nutrition_plan_repo

    async def get_by_id(self, plan_id: UUID) -> NutritionPlan | None:
        return await self._nutrition_plan_repo.find_by_id(plan_id)

    async def get_by_patient(self, patient_id: UUID) -> list[NutritionPlan]:
        return await self._nutrition_plan_repo.find_by_patient_id(patient_id)