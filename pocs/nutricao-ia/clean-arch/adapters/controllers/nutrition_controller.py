from typing import Any, Dict

from use_cases.generate_nutrition_plan import GenerateNutritionPlan, GenerateNutritionPlanInput


class NutritionController:
    def __init__(self, generate_plan: GenerateNutritionPlan) -> None:
        self._generate_plan = generate_plan

    def generate_plan(self, patient_id: str, exam_id: str) -> Dict[str, Any]:
        output = self._generate_plan.execute(
            GenerateNutritionPlanInput(patient_id=patient_id, exam_id=exam_id)
        )
        plan = output.plan
        return {
            "id": plan.id,
            "patient_id": plan.patient_id,
            "exam_id": plan.exam_id,
            "generated_at": plan.generated_at.isoformat(),
            "daily_calories_kcal": plan.daily_calories_kcal,
            "is_calorie_balanced": plan.is_calorie_balanced,
            "ai_rationale": plan.ai_rationale,
            "restrictions": plan.restrictions,
            "meals": [
                {
                    "name": m.name,
                    "time_suggestion": m.time_suggestion,
                    "foods": m.foods,
                    "calories_kcal": m.calories_kcal,
                    "notes": m.notes,
                }
                for m in plan.meals
            ],
            "nutrients": [
                {
                    "name": n.name,
                    "category": n.category.value,
                    "daily_target_g": n.daily_target_g,
                    "unit": n.unit,
                    "reason": n.reason,
                }
                for n in plan.nutrients
            ],
        }