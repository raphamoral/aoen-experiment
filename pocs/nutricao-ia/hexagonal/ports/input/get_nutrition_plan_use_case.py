from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.nutrition_plan import NutritionPlan


class GetNutritionPlanUseCasePort(ABC):
    @abstractmethod
    async def get_by_id(self, plan_id: UUID) -> NutritionPlan | None:
        ...

    @abstractmethod
    async def get_by_patient(self, patient_id: UUID) -> list[NutritionPlan]:
        ...