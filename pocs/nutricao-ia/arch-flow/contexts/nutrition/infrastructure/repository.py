from typing import List, Optional
from uuid import UUID

from sqlalchemy import Boolean, Column, Date, JSON, String, Text
from sqlalchemy.orm import Session

from shared.infra.database import Base
from contexts.nutrition.domain.entities import NutritionalPlan
from contexts.nutrition.domain.value_objects import (
    DailyIntakeTarget,
    FoodRestriction,
    MealDistribution,
    NutrientCategory,
)


class NutritionalPlanModel(Base):
    __tablename__ = "nutritional_plans"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    lab_result_id = Column(String(36), nullable=False)
    created_at = Column(Date, nullable=False)
    meal_distribution = Column(String(50), nullable=False)
    daily_targets_json = Column(JSON, nullable=False, default=list)
    food_restrictions_json = Column(JSON, nullable=False, default=list)
    clinical_notes = Column(Text, default="")
    is_active = Column(Boolean, default=True)


class NutritionalPlanRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, plan: NutritionalPlan) -> None:
        model = NutritionalPlanModel(
            id=str(plan.id),
            user_id=str(plan.user_id),
            lab_result_id=str(plan.lab_result_id),
            created_at=plan.created_at,
            meal_distribution=plan.meal_distribution.value,
            daily_targets_json=[
                {
                    "nutrient_name": t.nutrient_name,
                    "target_amount": t.target_amount,
                    "unit": t.unit,
                    "category": t.category.value,
                    "priority": t.priority,
                }
                for t in plan.daily_targets
            ],
            food_restrictions_json=[
                {
                    "food_group": r.food_group,
                    "reason": r.reason,
                    "is_absolute": r.is_absolute,
                }
                for r in plan.food_restrictions
            ],
            clinical_notes=plan.clinical_notes,
            is_active=plan.is_active,
        )
        self._session.merge(model)
        self._session.commit()

    def find_active_by_user(self, user_id: UUID) -> Optional[NutritionalPlan]:
        model = (
            self._session.query(NutritionalPlanModel)
            .filter_by(user_id=str(user_id), is_active=True)
            .order_by(NutritionalPlanModel.created_at.desc())
            .first()
        )
        return self._to_domain(model) if model else None

    def find_by_user(self, user_id: UUID) -> List[NutritionalPlan]:
        models = (
            self._session.query(NutritionalPlanModel)
            .filter_by(user_id=str(user_id))
            .order_by(NutritionalPlanModel.created_at.desc())
            .all()
        )
        return [self._to_domain(m) for m in models]

    def _to_domain(self, model: NutritionalPlanModel) -> NutritionalPlan:
        from uuid import UUID as _UUID

        plan = NutritionalPlan(
            id=_UUID(model.id),
            user_id=_UUID(model.user_id),
            lab_result_id=_UUID(model.lab_result_id),
            created_at=model.created_at,
            meal_distribution=MealDistribution(model.meal_distribution),
            clinical_notes=model.clinical_notes or "",
            is_active=model.is_active,
        )
        for t_data in model.daily_targets_json or []:
            plan.daily_targets.append(
                DailyIntakeTarget(
                    nutrient_name=t_data["nutrient_name"],
                    target_amount=t_data["target_amount"],
                    unit=t_data["unit"],
                    category=NutrientCategory(t_data["category"]),
                    priority=t_data.get("priority", "normal"),
                )
            )
        for r_data in model.food_restrictions_json or []:
            plan.food_restrictions.append(
                FoodRestriction(
                    food_group=r_data["food_group"],
                    reason=r_data["reason"],
                    is_absolute=r_data.get("is_absolute", True),
                )
            )
        return plan