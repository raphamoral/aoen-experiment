from datetime import datetime
from typing import List

from pydantic import BaseModel, field_validator


class ExamMarkerSchema(BaseModel):
    name: str
    value: float
    unit: str
    reference_min: float
    reference_max: float

    @field_validator("reference_max")
    @classmethod
    def validate_range(cls, v: float, info) -> float:
        ref_min = info.data.get("reference_min")
        if ref_min is not None and v <= ref_min:
            raise ValueError("reference_max deve ser maior que reference_min")
        return v


class ExamSubmitSchema(BaseModel):
    exam_date: datetime
    lab_name: str
    markers: List[ExamMarkerSchema]

    @field_validator("markers")
    @classmethod
    def validate_markers(cls, v: list) -> list:
        if not v:
            raise ValueError("Pelo menos um marcador é obrigatório")
        return v