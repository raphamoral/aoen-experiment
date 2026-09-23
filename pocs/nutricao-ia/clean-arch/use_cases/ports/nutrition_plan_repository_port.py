from abc import ABC, abstractmethod
from typing import List, Optional

from entities.nutrition_plan import NutritionPlan


class NutritionPlanRepositoryPort(ABC):

    @abstractmethod
    def save(self, plan: NutritionPlan) -> NutritionPlan: ...

    @abstractmethod
    def find_by_id(self, plan_id: str) -> Optional[NutritionPlan]: ...

    @abstractmethod
    def find_by_patient_id(self, patient_id: str) -> List[NutritionPlan]: ...

    @abstractmethod
    def find_latest_by_patient_id(self, patient_id: str) -> Optional[NutritionPlan]: ...