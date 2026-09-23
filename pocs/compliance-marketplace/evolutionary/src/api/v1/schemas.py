"""
Schemas de entrada/saída da API — separados dos modelos de domínio.

ADR-006: Anti-corruption layer na borda da API.
Domínio não vaza para fora; contratos de API evoluem independentemente.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from src.domain.models import ComplianceArea, ProjectStatus, ProposalStatus


class FreelancerCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    bio: str = Field(default="", max_length=2000)
    areas: List[ComplianceArea] = Field(..., min_length=1)
    hourly_rate_brl: float = Field(..., gt=0)


class FreelancerResponse(BaseModel):
    id: UUID
    name: str
    email: str
    bio: str
    areas: List[ComplianceArea]
    hourly_rate_brl: float
    reputation_score: float
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectCreate(BaseModel):
    client_id: UUID
    title: str = Field(..., min_length=5, max_length=500)
    description: str = Field(default="", max_length=5000)
    required_areas: List[ComplianceArea] = Field(..., min_length=1)
    budget_brl: float = Field(..., gt=0)
    deadline: Optional[datetime] = None


class ProjectResponse(BaseModel):
    id: UUID
    client_id: UUID
    title: str
    description: str
    required_areas: List[ComplianceArea]
    budget_brl: float
    deadline: Optional[datetime]
    status: ProjectStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class ProposalCreate(BaseModel):
    project_id: UUID
    freelancer_id: UUID
    cover_letter: str = Field(..., min_length=50, max_length=3000)
    proposed_rate_brl: float = Field(..., gt=0)
    estimated_hours: int = Field(..., gt=0)


class ProposalResponse(BaseModel):
    id: UUID
    project_id: UUID
    freelancer_id: UUID
    cover_letter: str
    proposed_rate_brl: float
    estimated_hours: int
    total_cost_brl: float
    status: ProposalStatus
    submitted_at: datetime

    model_config = {"from_attributes": True}