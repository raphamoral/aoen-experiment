from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, field_validator

from src.api.dependencies import get_user_repo
from src.models.user import ActivityLevel, Sex

router = APIRouter()


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    birth_date: date
    sex: Sex
    height_cm: float
    weight_kg: float
    activity_level: ActivityLevel = ActivityLevel.MODERATE
    health_goals: str | None = None

    @field_validator("height_cm")
    @classmethod
    def validate_height(cls, v: float) -> float:
        if v <= 0 or v > 300:
            raise ValueError("Altura deve estar entre 0 e 300 cm")
        return v

    @field_validator("weight_kg")
    @classmethod
    def validate_weight(cls, v: float) -> float:
        if v <= 0 or v > 500:
            raise ValueError("Peso deve estar entre 0 e 500 kg")
        return v


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    birth_date: date
    sex: Sex
    height_cm: float
    weight_kg: float
    activity_level: ActivityLevel
    health_goals: str | None

    model_config = {"from_attributes": True}


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(payload: UserCreate, repo=Depends(get_user_repo)):
    if await repo.get_by_email(payload.email):
        raise HTTPException(status_code=409, detail="Email já cadastrado")
    return await repo.create(**payload.model_dump())


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, repo=Depends(get_user_repo)):
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user


@router.get("/", response_model=list[UserResponse])
async def list_users(limit: int = 100, offset: int = 0, repo=Depends(get_user_repo)):
    return await repo.list(limit=limit, offset=offset)