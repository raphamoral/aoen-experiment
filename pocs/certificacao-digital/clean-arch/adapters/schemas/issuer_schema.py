from uuid import UUID

from pydantic import BaseModel, Field


class RegisterIssuerRequest(BaseModel):
    name: str = Field(..., min_length=1)
    document: str = Field(..., min_length=11, max_length=18, description="CPF or CNPJ (digits only or formatted)")


class IssuerResponse(BaseModel):
    id: UUID
    name: str
    document: str

    model_config = {"from_attributes": True}