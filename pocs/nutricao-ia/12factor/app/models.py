"""Modelos SQLAlchemy — schema do banco de dados."""
import uuid
from datetime import datetime
from sqlalchemy import String, Float, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    age: Mapped[int | None] = mapped_column(nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    exams: Mapped[list["LabExam"]] = relationship("LabExam", back_populates="user", cascade="all, delete-orphan")
    recommendations: Mapped[list["NutritionRecommendation"]] = relationship(
        "NutritionRecommendation", back_populates="user", cascade="all, delete-orphan"
    )


class LabExam(Base):
    __tablename__ = "lab_exams"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    exam_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    lab_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Marcadores armazenados como JSON — flexível para diferentes painéis de exames
    markers: Mapped[dict] = mapped_column(JSON, nullable=False)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="exams")
    recommendations: Mapped[list["NutritionRecommendation"]] = relationship(
        "NutritionRecommendation", back_populates="exam"
    )


class NutritionRecommendation(Base):
    __tablename__ = "nutrition_recommendations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    exam_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("lab_exams.id"), nullable=False)
    ai_model: Mapped[str] = mapped_column(String(100), nullable=False)  # rastreabilidade do modelo usado
    recommendations: Mapped[dict] = mapped_column(JSON, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="recommendations")
    exam: Mapped["LabExam"] = relationship("LabExam", back_populates="recommendations")