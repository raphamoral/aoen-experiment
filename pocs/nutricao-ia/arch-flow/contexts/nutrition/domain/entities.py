from dataclasses import dataclass, field
from datetime import date
from typing import List
from uuid import UUID

from shared.kernel.aggregate_root import AggregateRoot
from contexts.nutrition.domain.value_objects import (
    DailyIntakeTarget,
    FoodRestriction,
    MealDistribution,
)
from contexts.nutrition.domain.events import DeficiencyIdentified, NutritionalPlanCreated


@dataclass
class NutritionalPlan(AggregateRoot):
    """Plano Nutricional Personalizado — agregado raiz do contexto nutricional.

    Encapsula as recomendações nutricionais derivadas dos biomarcadores
    laboratoriais e do perfil de saúde do usuário.

    Wardley: Custom Build — a personalização baseada em exames é o
    diferencial; a infraestrutura nutricional tende ao commodity.
    A correlação biomarcador-nutriente é conhecimento proprietário.

    Team Topologies: Stream-aligned — co-evolui com o contexto
    laboratorial reagindo a eventos de biomarcadores alterados.
    """

    user_id: UUID
    lab_result_id: UUID
    created_at: date
    meal_distribution: MealDistribution
    daily_targets: List[DailyIntakeTarget] = field(default_factory=list)
    food_restrictions: List[FoodRestriction] = field(default_factory=list)
    clinical_notes: str = ""
    is_active: bool = True

    @classmethod
    def create(
        cls,
        user_id: UUID,
        lab_result_id: UUID,
        meal_distribution: MealDistribution,
        clinical_notes: str = "",
    ) -> "NutritionalPlan":
        plan = cls(
            user_id=user_id,
            lab_result_id=lab_result_id,
            created_at=date.today(),
            meal_distribution=meal_distribution,
            clinical_notes=clinical_notes,
        )
        plan.record_event(
            NutritionalPlanCreated(
                plan_id=plan.id,
                user_id=user_id,
                lab_result_id=lab_result_id,
            )
        )
        return plan

    def add_nutrient_target(self, target: DailyIntakeTarget) -> None:
        existing = next(
            (t for t in self.daily_targets if t.nutrient_name == target.nutrient_name),
            None,
        )
        if existing:
            self.daily_targets.remove(existing)
        self.daily_targets.append(target)

        if target.priority == "alta":
            self.record_event(
                DeficiencyIdentified(
                    plan_id=self.id,
                    user_id=self.user_id,
                    nutrient_name=target.nutrient_name,
                    priority=target.priority,
                )
            )

    def add_restriction(self, restriction: FoodRestriction) -> None:
        self.food_restrictions.append(restriction)

    def deactivate(self) -> None:
        self.is_active = False

    @property
    def high_priority_nutrients(self) -> List[DailyIntakeTarget]:
        return [t for t in self.daily_targets if t.priority == "alta"]