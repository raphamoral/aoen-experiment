from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from src.models.base import Base


class NutritionPlan(Base):
    """
    Plano nutricional gerado por IA para um usuário a partir de seus exames.

    Decisão (reversível): campos de lista armazenados como JSON.
    Permite evolução do schema de recomendações sem migração de banco.
    Normalizar em tabelas separadas quando queries complexas justificarem.
    """

    __tablename__ = "nutrition_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exam_panel_id = Column(Integer, ForeignKey("exam_panels.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    version = Column(Integer, nullable=False, default=1)

    deficiencies = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)
    restrictions = Column(JSON, default=list)
    supplements = Column(JSON, default=list)
    daily_calories = Column(Float)
    macros = Column(JSON)  # {"proteinas": 30, "carboidratos": 40, "gorduras": 30}
    ai_provider_used = Column(String(50))  # auditoria de qual provider gerou o plano

    user = relationship("User", back_populates="nutrition_plans")