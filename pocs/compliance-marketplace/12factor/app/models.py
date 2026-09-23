import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ComplianceDomain(str, PyEnum):
    LGPD = "LGPD"
    SOX = "SOX"
    ISO_27001 = "ISO_27001"
    PCI_DSS = "PCI_DSS"
    BACEN = "BACEN"
    CVM = "CVM"
    GDPR = "GDPR"
    HIPAA = "HIPAA"


class ProjectStatus(str, PyEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Freelancer(Base):
    __tablename__ = "freelancers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    bio: Mapped[str | None] = mapped_column(Text)
    hourly_rate: Mapped[float | None] = mapped_column(Numeric(10, 2))
    domains: Mapped[str | None] = mapped_column(Text)  # CSV de ComplianceDomain
    certifications: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    projects: Mapped[list["Project"]] = relationship("Project", back_populates="freelancer")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[ComplianceDomain] = mapped_column(SAEnum(ComplianceDomain), nullable=False)
    budget: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[ProjectStatus] = mapped_column(SAEnum(ProjectStatus), default=ProjectStatus.OPEN)
    client_email: Mapped[str] = mapped_column(String(255), nullable=False)
    freelancer_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("freelancers.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    freelancer: Mapped[Freelancer | None] = relationship("Freelancer", back_populates="projects")