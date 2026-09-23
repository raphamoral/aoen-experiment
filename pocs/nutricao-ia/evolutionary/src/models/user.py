from enum import Enum

from sqlalchemy import Column, Date, Enum as SAEnum, Float, Integer, String
from sqlalchemy.orm import relationship

from src.models.base import Base


class Sex(str, Enum):
    MALE = "masculino"
    FEMALE = "feminino"
    OTHER = "outro"


class ActivityLevel(str, Enum):
    SEDENTARY = "sedentario"
    LIGHT = "leve"
    MODERATE = "moderado"
    INTENSE = "intenso"
    VERY_INTENSE = "muito_intenso"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    birth_date = Column(Date, nullable=False)
    sex = Column(SAEnum(Sex), nullable=False)
    height_cm = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)
    activity_level = Column(SAEnum(ActivityLevel), nullable=False, default=ActivityLevel.MODERATE)
    health_goals = Column(String(500))

    exam_panels = relationship("ExamPanel", back_populates="user", cascade="all, delete-orphan")
    nutrition_plans = relationship(
        "NutritionPlan", back_populates="user", cascade="all, delete-orphan"
    )