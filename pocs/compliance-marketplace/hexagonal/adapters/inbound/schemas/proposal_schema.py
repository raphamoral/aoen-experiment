from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from domain.entities.proposal import ProposalStatus


class SubmitProposalRequest(BaseModel):
    project_id: UUID
    freelancer_id: UUID
    proposed_rate: Decimal = Field(..., gt=0, examples=[320.00])
    cover_letter: str = Field(..., min_length=50)
    estimated_hours: int = Field(..., gt=0, examples=[80])


class ProposalResponse(BaseModel):
    id: UUID
    project_id: UUID
    freelancer_id: UUID
    proposed_rate: Decimal
    cover_letter: str
    estimated_hours: int
    total_cost: Decimal
    status: ProposalStatus