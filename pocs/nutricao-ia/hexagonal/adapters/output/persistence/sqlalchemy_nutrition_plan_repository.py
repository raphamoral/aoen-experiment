from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from adapters.output.persistence.models import NutritionPlanModel
from domain.entities.nutrition_plan import DietaryRecommendation, NutritionPlan
from domain.value_objects.nutrient_level import NutrientLevel
from ports.output.nutrition_plan_repository_port import NutritionPlanRepositoryPort


class SQLAlchemyNutritionPlanRepository(NutritionPlanRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _recommendation_to_dict(self, rec: DietaryRecommendation) -> dict:
        return {
            "nutrient": rec.nutrient,
            "level": rec.level.value,
            "foods_to_increase": rec.foods_to_increase,
            "foods_to_avoid": rec.foods_to_avoid,
            "supplements": rec.supplements,
            "clinical_notes": rec.clinical_notes,
        }

    def _dict_to_recommendation(self, data: dict) -> DietaryRecommendation:
        return DietaryRecommendation(
            nutrient=data["nutrient"],
            level=NutrientLevel(data["level"]),
            foods_to_increase=data["foods_to_increase"],
            foods_to_avoid=data["foods_to_avoid"],
            supplements=data["supplements"],
            clinical_notes=data["clinical_notes"],
        )

    def _to_domain(self, model: NutritionPlanModel) -> NutritionPlan:
        return NutritionPlan(
            id=model.id,
            patient_id=model.patient_id,
            lab_exam_id=model.lab_exam_id,
            recommendations=[self._dict_to_recommendation(r) for r in model.recommendations],
            general_notes=model.general_notes,
            ai_analysis=model.ai_analysis,
            created_at=model.created_at,
        )

    def _to_model(self, plan: NutritionPlan) -> NutritionPlanModel:
        return NutritionPlanModel(
            id=plan.id,
            patient_id=plan.patient_id,
            lab_exam_id=plan.lab_exam_id,
            recommendations=[self._recommendation_to_dict(r) for r in plan.recommendations],
            general_notes=plan.general_notes,
            ai_analysis=plan.ai_analysis,
            created_at=plan.created_at,
        )

    async def save(self, plan: NutritionPlan) -> NutritionPlan:
        model = self._to_model(plan)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def find_by_id(self, plan_id: UUID) -> NutritionPlan | None:
        result = await self._session.execute(
            select(NutritionPlanModel).where(NutritionPlanModel.id == plan_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def find_by_patient_id(self, patient_id: UUID) -> list[NutritionPlan]:
        result = await self._session.execute(
            select(NutritionPlanModel).where(NutritionPlanModel.patient_id == patient_id)
        )
        return [self._to_domain(m) for m in result.scalars().all()]