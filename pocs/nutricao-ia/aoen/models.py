import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


def _gen_uuid() -> str:
    return str(uuid.uuid4())


class ExamStatus(PyEnum):
    PENDING = "pending"
    ANALYZED = "analyzed"
    ERROR = "error"


class PlanStatus(PyEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    EXPIRED = "expired"


class RecommendationCategory(PyEnum):
    FOOD = "food"
    SUPPLEMENT = "supplement"
    LIFESTYLE = "lifestyle"


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_gen_uuid)
    tenant_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    birth_date: Mapped[str] = mapped_column(String(10), nullable=False)   # YYYY-MM-DD
    sex: Mapped[str] = mapped_column(String(1), nullable=False)            # M/F
    weight_kg: Mapped[float] = mapped_column(Float, nullable=True)
    height_cm: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    exams: Mapped[list["LabExam"]] = relationship("LabExam", back_populates="patient")
    nutrition_plans: Mapped[list["NutritionPlan"]] = relationship(
        "NutritionPlan", back_populates="patient"
    )


class LabExam(Base):
    __tablename__ = "lab_exams"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_gen_uuid)
    patient_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("patients.id"), nullable=False, index=True
    )
    tenant_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    exam_date: Mapped[str] = mapped_column(String(10), nullable=False)  # YYYY-MM-DD
    lab_name: Mapped[str] = mapped_column(String(255), nullable=True)
    # JSON flexível: {nome_biomarcador: valor} — schema evolui sem migração de coluna
    biomarkers: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[ExamStatus] = mapped_column(Enum(ExamStatus), default=ExamStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    patient: Mapped["Patient"] = relationship("Patient", back_populates="exams")
    analysis: Mapped["ExamAnalysis"] = relationship(
        "ExamAnalysis", back_populates="exam", uselist=False
    )


class ExamAnalysis(Base):
    """Resultado persistido da análise do núcleo isolado — custo pago uma vez."""

    __tablename__ = "exam_analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_gen_uuid)
    exam_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("lab_exams.id"), nullable=False, unique=True
    )
    deficiencies: Mapped[list] = mapped_column(JSON, nullable=False)   # [{biomarker, value, ...}]
    excesses: Mapped[list] = mapped_column(JSON, nullable=False)        # [{biomarker, value, ...}]
    risk_scores: Mapped[dict] = mapped_column(JSON, nullable=False)     # {categoria: 0.0-1.0}
    overall_score: Mapped[float] = mapped_column(Float, nullable=False) # 0-100
    flags: Mapped[list] = mapped_column(JSON, default=list)             # flags clínicos
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    exam: Mapped["LabExam"] = relationship("LabExam", back_populates="analysis")
    nutrition_plans: Mapped[list["NutritionPlan"]] = relationship(
        "NutritionPlan", back_populates="analysis"
    )


class NutritionPlan(Base):
    __tablename__ = "nutrition_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_gen_uuid)
    patient_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("patients.id"), nullable=False, index=True
    )
    analysis_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("exam_analyses.id"), nullable=False
    )
    tenant_id: Mapped[str] = mapped_column(String(100), nullable=False)
    ai_narrative: Mapped[str] = mapped_column(Text, nullable=True)
    ai_model_used: Mapped[str] = mapped_column(String(100), nullable=True)
    status: Mapped[PlanStatus] = mapped_column(Enum(PlanStatus), default=PlanStatus.DRAFT)
    valid_until: Mapped[str] = mapped_column(String(10), nullable=True)  # YYYY-MM-DD
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    patient: Mapped["Patient"] = relationship("Patient", back_populates="nutrition_plans")
    analysis: Mapped["ExamAnalysis"] = relationship("ExamAnalysis", back_populates="nutrition_plans")
    recommendations: Mapped[list["NutritionRecommendation"]] = relationship(
        "NutritionRecommendation",
        back_populates="plan",
        order_by="NutritionRecommendation.priority",
    )


class NutritionRecommendation(Base):
    __tablename__ = "nutrition_recommendations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_gen_uuid)
    plan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("nutrition_plans.id"), nullable=False, index=True
    )
    category: Mapped[RecommendationCategory] = mapped_column(
        Enum(RecommendationCategory), nullable=False
    )
    priority: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 = mais urgente
    target_biomarker: Mapped[str] = mapped_column(String(100), nullable=True)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    plan: Mapped["NutritionPlan"] = relationship("NutritionPlan", back_populates="recommendations")