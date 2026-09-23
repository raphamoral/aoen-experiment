import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Column, String, Float, Integer, Boolean, DateTime,
    ForeignKey, JSON, Enum, Text, Numeric,
)
from sqlalchemy.orm import relationship

from database import Base


def new_uuid() -> str:
    return str(uuid.uuid4())


class ComplianceDomain(str, PyEnum):
    LGPD = "lgpd"
    SOX = "sox"
    ISO27001 = "iso27001"
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"
    GDPR = "gdpr"
    BACEN = "bacen"
    CVM = "cvm"
    SUSEP = "susep"
    ANVISA = "anvisa"


class ProjectStatus(str, PyEnum):
    DRAFT = "draft"
    OPEN = "open"
    MATCHING = "matching"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MatchStatus(str, PyEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    ACTIVE = "active"
    COMPLETED = "completed"


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(String, primary_key=True, default=new_uuid)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    plan = Column(String, default="starter")
    config = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    projects = relationship("Project", back_populates="tenant")
    usage_records = relationship("UsageRecord", back_populates="tenant")


class Freelancer(Base):
    __tablename__ = "freelancers"

    id = Column(String, primary_key=True, default=new_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    domains = Column(JSON, default=list)           # lista de ComplianceDomain
    certifications = Column(JSON, default=list)    # ex: ["CIPP/E", "CIPM", "CISA"]
    regulations_experience = Column(JSON, default=dict)  # {domain: years}
    hourly_rate = Column(Numeric(10, 2), nullable=False)
    availability_hours_week = Column(Integer, default=40)
    rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    portfolio_score = Column(Float, default=0.0)   # calculado pelo core
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    matches = relationship("Match", back_populates="freelancer")


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=new_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    required_domains = Column(JSON, default=list)
    required_certifications = Column(JSON, default=list)
    budget_min = Column(Numeric(10, 2))
    budget_max = Column(Numeric(10, 2))
    estimated_hours = Column(Integer)
    urgency_level = Column(Integer, default=3)     # 1-5
    status = Column(Enum(ProjectStatus), default=ProjectStatus.DRAFT)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    deadline = Column(DateTime, nullable=True)

    tenant = relationship("Tenant", back_populates="projects")
    matches = relationship("Match", back_populates="project")


class Match(Base):
    __tablename__ = "matches"

    id = Column(String, primary_key=True, default=new_uuid)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    freelancer_id = Column(String, ForeignKey("freelancers.id"), nullable=False)
    score = Column(Float, nullable=False)          # 0.0 - 1.0, gerado pelo core
    score_breakdown = Column(JSON, default=dict)   # detalhe por dimensão
    status = Column(Enum(MatchStatus), default=MatchStatus.PENDING)
    proposed_rate = Column(Numeric(10, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="matches")
    freelancer = relationship("Freelancer", back_populates="matches")


class UsageRecord(Base):
    __tablename__ = "usage_records"

    id = Column(String, primary_key=True, default=new_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    operation = Column(String, nullable=False)     # "match_run", "project_open", etc.
    units = Column(Integer, default=1)
    cost_credits = Column(Float, default=0.0)
    metadata = Column(JSON, default=dict)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="usage_records")