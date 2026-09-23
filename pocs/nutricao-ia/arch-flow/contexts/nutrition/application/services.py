import logging
from typing import List, Optional
from uuid import UUID

from shared.events.event_bus import event_bus
from contexts.nutrition.domain.entities import NutritionalPlan
from contexts.nutrition.domain.value_objects import (
    DailyIntakeTarget,
    MealDistribution,
    NutrientCategory,
)
from contexts.nutrition.infrastructure.repository import NutritionalPlanRepository

logger = logging.getLogger(__name__)

# Mapeamento de biomarcadores alterados para metas nutricionais terapêuticas.
# Representa o conhecimento clínico proprietário do produto.
# Wardley: Custom — este mapeamento é o diferencial do negócio.
BIOMARKER_NUTRIENT_MAP = {
    "Vitamina D": ("vitamina_d", 2000.0, "UI", NutrientCategory.VITAMIN, "alta"),
    "Ferro": ("ferro", 18.0, "mg", NutrientCategory.MINERAL, "alta"),
    "Ferritina": ("ferro", 18.0, "mg", NutrientCategory.MINERAL, "alta"),
    "Vitamina B12": ("vitamina_b12", 1000.0, "mcg", NutrientCategory.VITAMIN, "alta"),
    "Ácido Fólico": ("acido_folico", 400.0, "mcg", NutrientCategory.VITAMIN, "alta"),
    "Zinco": ("zinco", 11.0, "mg", NutrientCategory.MINERAL, "normal"),
    "Magnésio": ("magnesio", 320.0, "mg", NutrientCategory.MINERAL, "normal"),
    "Ômega-3": ("omega3", 2000.0, "mg", NutrientCategory.FATTY_ACID, "alta"),
    "Colesterol Total": ("fibra_solavel", 25.0, "g", NutrientCategory.MACRONUTRIENT, "normal"),
    "Glicose": ("carboidratos_complexos", 225.0, "g", NutrientCategory.MACRONUTRIENT, "normal"),
    "TSH": ("iodo", 150.0, "mcg", NutrientCategory.MINERAL, "alta"),
    "PCR": ("omega3", 3000.0, "mg", NutrientCategory.FATTY_ACID, "alta"),
    "Hemoglobina": ("ferro", 18.0, "mg", NutrientCategory.MINERAL, "alta"),
}


class NutritionalPlanService:
    """Serviço de Plano Nutricional.

    Traduz biomarcadores alterados em metas nutricionais terapêuticas,
    aplicando a linguagem ubíqua do domínio nutricional-clínico.
    """

    def __init__(self, repository: NutritionalPlanRepository) -> None:
        self._repo = repository

    async def generate_from_lab_result(
        self,
        user_id: UUID,
        lab_result_id: UUID,
        altered_biomarkers: List[dict],
        meal_distribution: MealDistribution = MealDistribution.BALANCED,
    ) -> NutritionalPlan:
        plan = NutritionalPlan.create(
            user_id=user_id,
            lab_result_id=lab_result_id,
            meal_distribution=meal_distribution,
            clinical_notes="Gerado automaticamente via análise de biomarcadores.",
        )

        for base in [
            DailyIntakeTarget("proteina", 1.6, "g/kg", NutrientCategory.MACRONUTRIENT),
            DailyIntakeTarget("agua", 35.0, "ml/kg", NutrientCategory.MACRONUTRIENT),
            DailyIntakeTarget("fibra_total", 25.0, "g", NutrientCategory.MACRONUTRIENT),
        ]:
            plan.add_nutrient_target(base)

        for biomarker in altered_biomarkers:
            mapping = BIOMARKER_NUTRIENT_MAP.get(biomarker["name"])
            if mapping:
                nutrient_name, amount, unit, category, priority = mapping
                plan.add_nutrient_target(
                    DailyIntakeTarget(
                        nutrient_name=nutrient_name,
                        target_amount=amount,
                        unit=unit,
                        category=category,
                        priority=priority,
                    )
                )

        self._repo.save(plan)

        for event in plan.pull_domain_events():
            await event_bus.publish(event)

        logger.info(
            "Plano nutricional %s gerado para usuário %s — %d metas, %d prioritárias",
            plan.id,
            user_id,
            len(plan.daily_targets),
            len(plan.high_priority_nutrients),
        )
        return plan

    def get_active_plan(self, user_id: UUID) -> Optional[NutritionalPlan]:
        return self._repo.find_active_by_user(user_id)

    def list_by_user(self, user_id: UUID) -> List[NutritionalPlan]:
        return self._repo.find_by_user(user_id)