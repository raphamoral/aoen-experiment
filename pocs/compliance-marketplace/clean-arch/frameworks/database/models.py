from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class FreelancerModel(Base):
    __tablename__ = "freelancers"

    id = Column(String(36), primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(254), unique=True, nullable=False, index=True)
    specialties = Column(Text, nullable=False)
    hourly_rate_amount = Column(String(20), nullable=False)
    hourly_rate_currency = Column(String(3), nullable=False, default="BRL")
    bio = Column(Text, nullable=False)
    years_of_experience = Column(Integer, nullable=False)
    certifications = Column(Text, nullable=False, default="")
    average_rating = Column(Float, nullable=True)
    total_reviews = Column(Integer, nullable=False, default=0)
    is_available = Column(Boolean, nullable=False, default=True)


class ClientModel(Base):
    __tablename__ = "clients"

    id = Column(String(36), primary_key=True)
    company_name = Column(String(300), nullable=False)
    email = Column(String(254), unique=True, nullable=False, index=True)
    cnpj = Column(String(18), unique=True, nullable=False)
    industry = Column(String(100), nullable=False)
    contact_name = Column(String(200), nullable=False)


class ProjectModel(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True)
    client_id = Column(String(36), nullable=False, index=True)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=False)
    required_specialties = Column(Text, nullable=False)
    budget_amount = Column(String(20), nullable=False)
    budget_currency = Column(String(3), nullable=False, default="BRL")
    deadline = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False, default="OPEN", index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class ProposalModel(Base):
    __tablename__ = "proposals"

    id = Column(String(36), primary_key=True)
    project_id = Column(String(36), nullable=False, index=True)
    freelancer_id = Column(String(36), nullable=False, index=True)
    proposed_rate_amount = Column(String(20), nullable=False)
    proposed_rate_currency = Column(String(3), nullable=False, default="BRL")
    cover_letter = Column(Text, nullable=False)
    estimated_hours = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="PENDING", index=True)
    submitted_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class ContractModel(Base):
    __tablename__ = "contracts"

    id = Column(String(36), primary_key=True)
    project_id = Column(String(36), nullable=False, unique=True, index=True)
    freelancer_id = Column(String(36), nullable=False, index=True)
    client_id = Column(String(36), nullable=False, index=True)
    proposal_id = Column(String(36), nullable=False, unique=True)
    agreed_rate_amount = Column(String(20), nullable=False)
    agreed_rate_currency = Column(String(3), nullable=False, default="BRL")
    estimated_hours = Column(Integer, nullable=False)
    total_value_amount = Column(String(20), nullable=False)
    total_value_currency = Column(String(3), nullable=False, default="BRL")
    signed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    is_active = Column(Boolean, nullable=False, default=True)