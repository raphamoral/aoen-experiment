from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from domain.entities.nutrition_plan import NutritionPlan


@dataclass
class GenerateNutritionPlanCommand:
    patient_id: UUID
    lab_exam_id: UUID


class GenerateNutritionPlanUseCasePort(ABC):
    @abstractmethod
    async def execute(self, command: GenerateNutritionPlanCommand) -> NutritionPlan:
        ...