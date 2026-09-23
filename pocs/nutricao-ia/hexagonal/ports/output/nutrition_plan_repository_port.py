from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.nutrition_plan import NutritionPlan


class NutritionPlanRepositoryPort(ABC):
    @abstractmethod
    async def save(self, plan: NutritionPlan) -> NutritionPlan:
        ...

    @abstractmethod
    async def find_by_id(self, plan_id: UUID) -> NutritionPlan | None:
        ...

    @abstractmethod
    async def find_by_patient_id(self, patient_id: UUID) -> list[NutritionPlan]:
        ...