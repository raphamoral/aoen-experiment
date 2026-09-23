from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from domain.entities.project import ProjectStatus
from domain.value_objects.compliance_area import ComplianceArea


class CreateProjectRequest(BaseModel):
    title: str = Field(..., min_length=5, examples=["Adequação LGPD – Fintech"])
    description: str = Field(..., min_length=20)
    client_id: UUID
    required_areas: List[ComplianceArea] = Field(..., min_length=1)
    budget: Decimal = Field(..., gt=0, examples=[15000.00])
    deadline: date


class ProjectResponse(BaseModel):
    id: UUID
    title: str
    description: str
    client_id: UUID
    required_areas: List[ComplianceArea]
    budget: Decimal
    deadline: date
    status: ProjectStatus
    assigned_freelancer_id: Optional[UUID]