from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import Column, DateTime, JSON, String, Text
from sqlalchemy.orm import Session

from shared.infra.database import Base
from contexts.ai_analysis.domain.entities import PersonalizedAnalysis
from contexts.ai_analysis.domain.value_objects import (
    HealthInsight,
    InsightCategory,
    RiskLevel,
)


class AnalysisModel(Base):
    __tablename__ = "personalized_analyses"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    lab_result_id = Column(String(36), nullable=False, index=True)
    generated_at = Column(DateTime, nullable=False)
    insights_json = Column(JSON, nullable=False, default=list)
    summary = Column(Text, default="")
    model_used = Column(String(100), default="")


class AnalysisRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, analysis: PersonalizedAnalysis) -> None:
        model = AnalysisModel(
            id=str(analysis.id),
            user_id=str(analysis.user_id),
            lab_result_id=str(analysis.lab_result_id),
            generated_at=analysis.generated_at,
            insights_json=[
                {
                    "title": i.title,
                    "description": i.description,
                    "risk_level": i.risk_level.value,
                    "category": i.category.value,
                    "biomarkers_involved": i.biomarkers_involved,
                    "recommendation": i.recommendation,
                    "evidence_basis": i.evidence_basis,
                }
                for i in analysis.insights
            ],
            summary=analysis.summary,
            model_used=analysis.model_used,
        )
        self._session.merge(model)
        self._session.commit()

    def find_by_id(self, analysis_id: UUID) -> Optional[PersonalizedAnalysis]:
        model = (
            self._session.query(AnalysisModel)
            .filter_by(id=str(analysis_id))
            .first()
        )
        return self._to_domain(model) if model else None

    def find_by_lab_result(self, lab_result_id: UUID) -> Optional[PersonalizedAnalysis]:
        model = (
            self._session.query(AnalysisModel)
            .filter_by(lab_result_id=str(lab_result_id))
            .order_by(AnalysisModel.generated_at.desc())
            .first()
        )
        return self._to_domain(model) if model else None

    def find_by_user(self, user_id: UUID) -> List[PersonalizedAnalysis]:
        models = (
            self._session.query(AnalysisModel)
            .filter_by(user_id=str(user_id))
            .order_by(AnalysisModel.generated_at.desc())
            .all()
        )
        return [self._to_domain(m) for m in models]

    def _to_domain(self, model: AnalysisModel) -> PersonalizedAnalysis:
        from uuid import UUID as _UUID

        analysis = PersonalizedAnalysis(
            id=_UUID(model.id),
            user_id=_UUID(model.user_id),
            lab_result_id=_UUID(model.lab_result_id),
            generated_at=model.generated_at,
            summary=model.summary or "",
            model_used=model.model_used or "",
        )
        for i_data in model.insights_json or []:
            try:
                analysis.insights.append(
                    HealthInsight(
                        title=i_data["title"],
                        description=i_data["description"],
                        risk_level=RiskLevel(i_data["risk_level"]),
                        category=InsightCategory(i_data["category"]),
                        biomarkers_involved=i_data.get("biomarkers_involved", []),
                        recommendation=i_data["recommendation"],
                        evidence_basis=i_data.get("evidence_basis", ""),
                    )
                )
            except (ValueError, KeyError):
                pass
        return analysis