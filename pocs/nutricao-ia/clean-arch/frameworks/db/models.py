from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

try:
    from sqlalchemy.dialects.sqlite import JSON
except ImportError:
    from sqlalchemy import JSON  # type: ignore

from frameworks.db.connection import Base


class PatientModel(Base):
    __tablename__ = "patients"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    birth_date = Column(String, nullable=False)  # ISO-8601 string para portabilidade
    gender = Column(String, nullable=False)
    weight_kg = Column(Float, nullable=False)
    height_cm = Column(Float, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

    exams = relationship("ExamModel", back_populates="patient")
    nutrition_plans = relationship("NutritionPlanModel", back_populates="patient")


class ExamModel(Base):
    __tablename__ = "exams"

    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)
    exam_date = Column(DateTime, nullable=False)
    lab_name = Column(String, nullable=False)
    markers = Column(JSON, nullable=False, default=list)

    patient = relationship("PatientModel", back_populates="exams")
    nutrition_plans = relationship("NutritionPlanModel", back_populates="exam")


class NutritionPlanModel(Base):
    __tablename__ = "nutrition_plans"

    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)
    exam_id = Column(String, ForeignKey("exams.id"), nullable=False)
    generated_at = Column(DateTime, nullable=False)
    daily_calories_kcal = Column(Float, nullable=False)
    meals = Column(JSON, nullable=False, default=list)
    nutrients = Column(JSON, nullable=False, default=list)
    restrictions = Column(JSON, nullable=False, default=list)
    ai_rationale = Column(Text, nullable=False, default="")
    version = Column(Integer, nullable=False, default=1)

    patient = relationship("PatientModel", back_populates="nutrition_plans")
    exam = relationship("ExamModel", back_populates="nutrition_plans")