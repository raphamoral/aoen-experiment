from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from domain.value_objects.compliance_area import ComplianceArea
from domain.value_objects.expertise_level import ExpertiseLevel


class RegisterFreelancerRequest(BaseModel):
    name: str = Field(..., min_length=2, examples=["Ana Souza"])
    email: EmailStr = Field(..., examples=["ana@compliance.com.br"])
    compliance_areas: List[ComplianceArea] = Field(..., min_length=1)
    expertise_level: ExpertiseLevel
    hourly_rate: Decimal = Field(..., gt=0, examples=[350.00])
    currency: str = Field("BRL", pattern="^(BRL|USD|EUR)$")
    bio: str = Field(..., min_length=10)
    certifications: List[str] = Field(default_factory=list)


class UpdateAvailabilityRequest(BaseModel):
    available: bool


class RateFreelancerRequest(BaseModel):
    rating: float = Field(..., ge=0.0, le=5.0)


class FreelancerResponse(BaseModel):
    id: UUID
    name: str
    email: str
    compliance_areas: List[ComplianceArea]
    expertise_level: ExpertiseLevel
    hourly_rate: Decimal
    currency: str
    bio: str
    certifications: List[str]
    is_available: bool
    rating: Optional[float]