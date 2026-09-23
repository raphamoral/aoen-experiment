from datetime import date, datetime
from uuid import UUID

from sqlalchemy import JSON, Date, DateTime, Integer, String, Text, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class PatientModel(Base):
    __tablename__ = "patients"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(1), nullable=False)
    health_goals: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class LabExamModel(Base):
    __tablename__ = "lab_exams"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    patient_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), index=True, nullable=False)
    exam_date: Mapped[date] = mapped_column(Date, nullable=False)
    results: Mapped[list] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class NutritionPlanModel(Base):
    __tablename__ = "nutrition_plans"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    patient_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), index=True, nullable=False)
    lab_exam_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), index=True, nullable=False)
    recommendations: Mapped[list] = mapped_column(JSON, nullable=False)
    general_notes: Mapped[str] = mapped_column(Text, nullable=False)
    ai_analysis: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)