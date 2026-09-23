import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models import ComplianceDomain, ProjectStatus


# --- Auth ---

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# --- Freelancer ---

class FreelancerCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)
    password: str = Field(min_length=8)
    bio: str | None = None
    hourly_rate: float | None = Field(default=None, gt=0)
    domains: list[ComplianceDomain] = []
    certifications: list[str] = []


class FreelancerResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    bio: str | None
    hourly_rate: float | None
    domains: list[str]
    certifications: list[str]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class FreelancerUpdate(BaseModel):
    bio: str | None = None
    hourly_rate: float | None = Field(default=None, gt=0)
    domains: list[ComplianceDomain] | None = None
    certifications: list[str] | None = None


# --- Project ---

class ProjectCreate(BaseModel):
    title: str = Field(min_length=5, max_length=500)
    description: str = Field(min_length=20)
    domain: ComplianceDomain
    budget: float = Field(gt=0)
    client_email: EmailStr


class ProjectResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    domain: ComplianceDomain
    budget: float
    status: ProjectStatus
    client_email: EmailStr
    freelancer_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=5)
    description: str | None = None
    budget: float | None = Field(default=None, gt=0)
    status: ProjectStatus | None = None