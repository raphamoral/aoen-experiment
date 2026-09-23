from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from entities.nutrient import Nutrient


@dataclass
class Meal:
    name: str
    time_suggestion: str
    foods: List[str]
    calories_kcal: float
    notes: str = ""


@dataclass
class NutritionPlan:
    id: str
    patient_id: str
    exam_id: str
    generated_at: datetime
    daily_calories_kcal: float
    meals: List[Meal] = field(default_factory=list)
    nutrients: List[Nutrient] = field(default_factory=list)
    restrictions: List[str] = field(default_factory=list)
    ai_rationale: str = ""
    version: int = 1

    @property
    def total_meals_calories(self) -> float:
        return sum(m.calories_kcal for m in self.meals)

    @property
    def is_calorie_balanced(self) -> bool:
        tolerance = self.daily_calories_kcal * 0.10
        return abs(self.total_meals_calories - self.daily_calories_kcal) <= tolerance

    def validate(self) -> None:
        if self.daily_calories_kcal <= 0:
            raise ValueError("Calorias diárias devem ser positivas")
        if not self.meals:
            raise ValueError("Plano nutricional deve ter pelo menos uma refeição")
        if not self.ai_rationale.strip():
            raise ValueError("Justificativa da IA é obrigatória no plano nutricional")