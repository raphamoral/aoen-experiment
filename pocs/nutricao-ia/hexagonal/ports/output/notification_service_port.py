from abc import ABC, abstractmethod

from domain.entities.nutrition_plan import NutritionPlan
from domain.entities.patient import Patient


class NotificationServicePort(ABC):
    """Secondary port (driven) for patient notifications."""

    @abstractmethod
    async def send_welcome(self, patient: Patient) -> None:
        ...

    @abstractmethod
    async def send_plan_ready(
        self, patient: Patient, plan: NutritionPlan
    ) -> None:
        ...