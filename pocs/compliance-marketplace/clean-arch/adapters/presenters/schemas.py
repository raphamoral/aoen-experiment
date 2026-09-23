from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class ComplianceAreaEnum(str, Enum):
    LGPD = "LGPD"
    GDPR = "GDPR"
    SOX = "SOX"
    ISO_27001 = "ISO_27001"
    PCI_DSS = "PCI_DSS"
    BACEN = "BACEN"
    CVM = "CVM"
    HIPAA = "HIPAA"
    COBIT = "COBIT"
    FEBRABAN = "FEBRABAN"


# --- Freelancer ---

class FreelancerCreateRequest(BaseModel):
    name: str = Field(..., min_length=2)
    email: str
    specializations: List[ComplianceAreaEnum] = Field(..., min_length=1)
    hourly_rate: float = Field(..., gt=0)
    bio: str = Field(..., min_length=10)


class FreelancerResponse(BaseModel):
    id: str
    name: str
    email: str
    specializations: List[str]
    hourly_rate: float
    bio: str
    rating: float
    total_reviews: int
    is_active: bool


# --- Client ---

class ClientCreateRequest(BaseModel):
    name: str = Field(..., min_length=2)
    email: str
    company: str = Field(..., min_length=2)
    industry: str


class ClientResponse(BaseModel):
    id: str
    name: str
    email: str
    company: str
    industry: str
    is_active: bool


# --- Project ---

class ProjectCreateRequest(BaseModel):
    title: str = Field(..., min_length=3)
    description: str
    budget: float = Field(..., gt=0)
    compliance_areas: List[ComplianceAreaEnum] = Field(..., min_length=1)
    client_id: str


class ProjectResponse(BaseModel):
    id: str
    title: str
    description: str
    budget: float
    compliance_areas: List[str]
    client_id: str
    status: str
    created_at: str


# --- Proposal ---

class ProposalCreateRequest(BaseModel):
    project_id: str
    freelancer_id: str
    price: float = Field(..., gt=0)
    cover_letter: str = Field(..., min_length=10)
    estimated_days: int = Field(..., gt=0)


class ProposalAcceptRequest(BaseModel):
    client_id: str


class ProposalResponse(BaseModel):
    id: str
    project_id: str
    freelancer_id: str
    price: float
    cover_letter: str
    estimated_days: int
    status: str
    submitted_at: str


# --- Contract ---

class ContractResponse(BaseModel):
    id: str
    project_id: str
    proposal_id: str
    freelancer_id: str
    client_id: str
    agreed_price: float
    estimated_days: int
    status: str
    created_at: str
    completed_at: Optional[str]