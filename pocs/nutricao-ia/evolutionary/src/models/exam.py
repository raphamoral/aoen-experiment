from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.models.base import Base


class ExamPanel(Base):
    """Conjunto de exames realizados em uma única coleta laboratorial."""

    __tablename__ = "exam_panels"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exam_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    lab_name = Column(String(200))
    notes = Column(String(500))

    user = relationship("User", back_populates="exam_panels")
    results = relationship("ExamResult", back_populates="panel", cascade="all, delete-orphan")


class ExamResult(Base):
    """Resultado de um marcador laboratorial específico."""

    __tablename__ = "exam_results"

    id = Column(Integer, primary_key=True, index=True)
    panel_id = Column(Integer, ForeignKey("exam_panels.id"), nullable=False)
    marker_name = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(20))
    reference_min = Column(Float)
    reference_max = Column(Float)

    panel = relationship("ExamPanel", back_populates="results")

    @property
    def status(self) -> str:
        if self.reference_min is not None and self.value < self.reference_min:
            return "baixo"
        if self.reference_max is not None and self.value > self.reference_max:
            return "alto"
        return "normal"