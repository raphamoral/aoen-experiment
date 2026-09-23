from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from entities.nutrient import Nutrient, NutrientCategory
from entities.nutrition_plan import Meal, NutritionPlan
from frameworks.db.models import NutritionPlanModel
from use_cases.ports.nutrition_plan_repository_port import NutritionPlanRepositoryPort


class SqlAlchemyNutritionPlanRepository(NutritionPlanRepositoryPort):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, plan: NutritionPlan) -> NutritionPlan:
        self._session.add(
            NutritionPlanModel(
                id=plan.id,
                patient_id=plan.patient_id,
                exam_id=plan.exam_id,
                generated_at=plan.generated_at,
                daily_calories_kcal=plan.daily_calories_kcal,
                meals=[
                    {
                        "name": m.name,
                        "time_suggestion": m.time_suggestion,
                        "foods": m.foods,
                        "calories_kcal": m.calories_kcal,
                        "notes": m.notes,
                    }
                    for m in plan.meals
                ],
                nutrients=[
                    {
                        "name": n.name,
                        "category": n.category.value,
                        "daily_target_g": n.daily_target_g,
                        "unit": n.unit,
                        "reason": n.reason,
                    }
                    for n in plan.nutrients
                ],
                restrictions=plan.restrictions,
                ai_rationale=plan.ai_rationale,
                version=plan.version,
            )
        )
        self._session.commit()
        return plan

    def find_by_id(self, plan_id: str) -> Optional[NutritionPlan]:
        model = self._session.query(NutritionPlanModel).filter_by(id=plan_id).first()
        return self._to_entity(model) if model else None

    def find_by_patient_id(self, patient_id: str) -> List[NutritionPlan]:
        models = (
            self._session.query(NutritionPlanModel)
            .filter_by(patient_id=patient_id)
            .order_by(NutritionPlanModel.generated_at.desc())
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_latest_by_patient_id(self, patient_id: str) -> Optional[NutritionPlan]:
        model = (
            self._session.query(NutritionPlanModel)
            .filter_by(patient_id=patient_id)
            .order_by(NutritionPlanModel.generated_at.desc())
            .first()
        )
        return self._to_entity(model) if model else None

    def _to_entity(self, model: NutritionPlanModel) -> NutritionPlan:
        return NutritionPlan(
            id=model.id,
            patient_id=model.patient_id,
            exam_id=model.exam_id,
            generated_at=model.generated_at
            if isinstance(model.generated_at, datetime)
            else datetime.fromisoformat(str(model.generated_at)),
            daily_calories_kcal=model.daily_calories_kcal,
            meals=[
                Meal(
                    name=m["name"],
                    time_suggestion=m["time_suggestion"],
                    foods=m["foods"],
                    calories_kcal=m["calories_kcal"],
                    notes=m.get("notes", ""),
                )
                for m in model.meals
            ],
            nutrients=[
                Nutrient(
                    name=n["name"],
                    category=NutrientCategory(n["category"]),
                    daily_target_g=n["daily_target_g"],
                    unit=n["unit"],
                    reason=n["reason"],
                )
                for n in model.nutrients
            ],
            restrictions=model.restrictions,
            ai_rationale=model.ai_rationale,
            version=model.version,
        )