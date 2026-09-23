from sqlalchemy import Column, String, Float, Integer, Boolean, JSON
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class FreelancerModel(Base):
    __tablename__ = "freelancers"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    specializations = Column(JSON, nullable=False)
    hourly_rate = Column(Float, nullable=False)
    bio = Column(String, nullable=False)
    rating = Column(Float, default=0.0, nullable=False)
    total_reviews = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


class ClientModel(Base):
    __tablename__ = "clients"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    company = Column(String, nullable=False)
    industry = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


class ProjectModel(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    budget = Column(Float, nullable=False)
    compliance_areas = Column(JSON, nullable=False)
    client_id = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, default="OPEN")
    created_at = Column(String, nullable=False)


class ProposalModel(Base):
    __tablename__ = "proposals"

    id = Column(String, primary_key=True)
    project_id = Column(String, nullable=False, index=True)
    freelancer_id = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)
    cover_letter = Column(String, nullable=False)
    estimated_days = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="PENDING")
    submitted_at = Column(String, nullable=False)


class ContractModel(Base):
    __tablename__ = "contracts"

    id = Column(String, primary_key=True)
    project_id = Column(String, nullable=False, index=True)
    proposal_id = Column(String, nullable=False)
    freelancer_id = Column(String, nullable=False, index=True)
    client_id = Column(String, nullable=False, index=True)
    agreed_price = Column(Float, nullable=False)
    estimated_days = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="ACTIVE")
    created_at = Column(String, nullable=False)
    completed_at = Column(String, nullable=True)