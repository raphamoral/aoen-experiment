from datetime import date

from pydantic import BaseModel, EmailStr, field_validator


class PatientCreateSchema(BaseModel):
    name: str
    birth_date: date
    gender: str
    weight_kg: float
    height_cm: float
    email: EmailStr

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        if v.lower() not in {"male", "female", "other"}:
            raise ValueError("gender deve ser: male, female ou other")
        return v.lower()

    @field_validator("weight_kg")
    @classmethod
    def validate_weight(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Peso deve ser positivo")
        return v

    @field_validator("height_cm")
    @classmethod
    def validate_height(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Altura deve ser positiva")
        return v