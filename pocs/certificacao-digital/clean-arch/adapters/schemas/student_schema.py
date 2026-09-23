from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterStudentRequest(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr


class StudentResponse(BaseModel):
    id: UUID
    name: str
    email: str

    model_config = {"from_attributes": True}