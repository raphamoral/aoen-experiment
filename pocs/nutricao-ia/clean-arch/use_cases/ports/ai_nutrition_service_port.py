from abc import ABC, abstractmethod

from entities.exam import Exam
from entities.nutrition_plan import NutritionPlan
from entities.patient import Patient


class AiNutritionServicePort(ABC):

    @abstractmethod
    def generate_plan(self, patient: Patient, exam: Exam) -> NutritionPlan: ...