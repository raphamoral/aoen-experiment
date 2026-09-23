from uuid import UUID

from pydantic import BaseModel, Field


class RegisterCourseRequest(BaseModel):
    name: str = Field(..., min_length=1)
    description: str
    issuer_id: UUID
    workload_hours: int = Field(..., gt=0)


class CourseResponse(BaseModel):
    id: UUID
    name: str
    description: str
    issuer_id: UUID
    workload_hours: int

    model_config = {"from_attributes": True}