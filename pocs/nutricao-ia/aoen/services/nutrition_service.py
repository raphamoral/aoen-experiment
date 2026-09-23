import uuid
from datetime import date, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_tenant_config
from core.analyzer import AnalysisResult, BiomarkerDeviation, Severity
from core.nutrition_engine import NutritionPlanData, generate_plan
from models import (
    ExamAnalysis,
    NutritionPlan,
    NutritionRecommendation,
    PlanStatus,
    RecommendationCategory,
)
from services.ai_service import AIService


def _rebuild_analysis_result(exam_analysis: ExamAnalysis) -> AnalysisResult:
    """Reconstrói AnalysisResult a partir do JSON persistido para uso no core/."""

    def _to_deviation(d: dict, dev_type: str) -> BiomarkerDeviation:
        return BiomarkerDeviation(
            biomarker=d["biomarker"],
            value=d["value"],
            unit=d["unit"],
            reference_min=d["reference_min"],
            reference_max=d["reference_max"],
            deviation_type=dev_type,
            deviation_percent=d["deviation_percent"],
            severity=Severity(d["severity"]),
        )

    return AnalysisResult(
        exam_id=exam_analysis.exam_id,
        deficiencies=[_to_deviation(d, "deficiency") for d in exam_analysis.deficiencies],
        excesses=[_to_deviation(d, "excess") for d in exam_analysis.excesses],
        risk_scores=exam_analysis.risk_scores,
        overall_score=exam_analysis.overall_score,
        flags=exam_analysis.flags,
    )


class NutritionService:
    """
    FASE 2 — SERVICE LAYER: orquestra geração de plano nutricional.
    Combina core/ (regras) + AIService (narrativa) sem expor isso ao router.
    """

    def __init__(self, db: AsyncSession, ai_service: AIService):
        self.db = db
        self.ai_service = ai_service

    async def generate_nutrition_plan(
        self,
        patient_id: str,
        analysis_id: str,
        tenant_id: str,
    ) -> NutritionPlan:
        result = await self.db.execute(
            select(ExamAnalysis).where(ExamAnalysis.id == analysis_id)
        )
        exam_analysis = result.scalar_one_or_none()
        if not exam_analysis:
            raise ValueError(f"Analysis {analysis_id} not found")

        # FASE 3 — CONFIG-DRIVEN: comportamento do plano controlado por tenant
        tenant_cfg = get_tenant_config(tenant_id)

        analysis_result = _rebuild_analysis_result(exam_analysis)

        # Núcleo gera recomendações estruturadas (sem IA, sem DB)
        plan_data: NutritionPlanData = generate_plan(
            analysis=analysis_result,
            include_supplements=tenant_cfg.include_supplement_recommendations,
            include_lifestyle=tenant_cfg.include_lifestyle_recommendations,
        )

        # IA gera narrativa humanizada (custo medido por chamada por tenant)
        ai_narrative = await self.ai_service.generate_nutrition_narrative(
            analysis_result=analysis_result,
            plan_data=plan_data,
            language=tenant_cfg.report_language,
            model=tenant_cfg.ai_model,
        )

        valid_until = (date.today() + timedelta(days=90)).isoformat()

        plan = NutritionPlan(
            id=str(uuid.uuid4()),
            patient_id=patient_id,
            analysis_id=analysis_id,
            tenant_id=tenant_id,
            ai_narrative=ai_narrative,
            ai_model_used=tenant_cfg.ai_model,
            status=PlanStatus.ACTIVE,
            valid_until=valid_until,
        )
        self.db.add(plan)
        await self.db.flush()

        for rec_data in plan_data.recommendations:
            rec = NutritionRecommendation(
                id=str(uuid.uuid4()),
                plan_id=plan.id,
                category=RecommendationCategory(rec_data.category.value),
                priority=rec_data.priority,
                target_biomarker=rec_data.target_biomarker,
                recommendation=rec_data.recommendation,
                rationale=rec_data.rationale,
            )
            self.db.add(rec)

        await self.db.flush()
        return plan

    async def get_plan_by_id(self, plan_id: str, tenant_id: str) -> Optional[NutritionPlan]:
        result = await self.db.execute(
            select(NutritionPlan).where(
                NutritionPlan.id == plan_id, NutritionPlan.tenant_id == tenant_id
            )
        )
        return result.scalar_one_or_none()

    async def get_patient_plans(self, patient_id: str, tenant_id: str) -> list[NutritionPlan]:
        result = await self.db.execute(
            select(NutritionPlan)
            .where(
                NutritionPlan.patient_id == patient_id,
                NutritionPlan.tenant_id == tenant_id,
            )
            .order_by(NutritionPlan.created_at.desc())
        )
        return list(result.scalars().all())