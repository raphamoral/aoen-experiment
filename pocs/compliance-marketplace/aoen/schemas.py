from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, EmailStr


class TenantCreate(BaseModel):
    name: str
    slug: str
    plan: str = "starter"
    config: dict[str, Any] = {}


class TenantOut(BaseModel):
    id: str
    name: str
    slug: str
    plan: str
    config: dict[str, Any]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class FreelancerCreate(BaseModel):
    name: str
    email: EmailStr
    domains: list[str] = []
    certifications: list[str] = []
    regulations_experience: dict[str, int] = {}
    hourly_rate: Decimal
    availability_hours_week: int = 40


class FreelancerUpdate(BaseModel):
    domains: list[str] | None = None
    certifications: list[str] | None = None
    regulations_experience: dict[str, int] | None = None
    hourly_rate: Decimal | None = None
    availability_hours_week: int | None = None


class FreelancerOut(BaseModel):
    id: str
    tenant_id: str
    name: str
    email: str
    domains: list[str]
    certifications: list[str]
    regulations_experience: dict[str, int]
    hourly_rate: Decimal
    availability_hours_week: int
    rating: float
    portfolio_score: float
    is_active: bool

    class Config:
        from_attributes = True


class ProjectCreate(BaseModel):
    title: str
    description: str
    required_domains: list[str] = []
    required_certifications: list[str] = []
    budget_min: Decimal | None = None
    budget_max: Decimal | None = None
    estimated_hours: int | None = None
    urgency_level: int = 3
    deadline: datetime | None = None


class ProjectUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    required_domains: list[str] | None = None
    required_certifications: list[str] | None = None
    budget_min: Decimal | None = None
    budget_max: Decimal | None = None
    estimated_hours: int | None = None
    urgency_level: int | None = None
    deadline: datetime | None = None


class ProjectOut(BaseModel):
    id: str
    tenant_id: str
    title: str
    description: str
    required_domains: list[str]
    required_certifications: list[str]
    budget_min: Decimal | None
    budget_max: Decimal | None
    estimated_hours: int | None
    urgency_level: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class MatchOut(BaseModel):
    id: str
    project_id: str
    freelancer_id: str
    score: float
    score_breakdown: dict[str, Any]
    status: str
    proposed_rate: Decimal | None
    created_at: datetime

    class Config:
        from_attributes = True