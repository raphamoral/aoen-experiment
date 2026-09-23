from datetime import date
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from shared.infra.database import get_db
from contexts.user_profile.application.services import UserProfileService
from contexts.user_profile.infrastructure.repository import UserProfileRepository

router = APIRouter(prefix="/users", tags=["Perfis de Usuário"])


class CreateProfileInput(BaseModel):
    full_name: str
    email: str
    biological_sex: str
    birth_date: date


class AddGoalInput(BaseModel):
    goal: str


class AddConditionInput(BaseModel):
    condition_name: str
    is_chronic: bool = False


class HealthConditionOutput(BaseModel):
    name: str
    is_chronic: bool


class UserProfileOutput(BaseModel):
    id: str
    full_name: str
    email: str
    biological_sex: str
    birth_date: date
    age: int
    age_group: str
    health_goals: List[str]
    health_conditions: List[HealthConditionOutput]
    is_active: bool


def get_service(db: Session = Depends(get_db)) -> UserProfileService:
    return UserProfileService(UserProfileRepository(db))


@router.post("/", response_model=UserProfileOutput, status_code=status.HTTP_201_CREATED)
async def create_profile(
    payload: CreateProfileInput,
    service: UserProfileService = Depends(get_service),
):
    """Cria Perfil do Usuário.

    Ponto de entrada do fluxo de valor: sem perfil, não há personalização.
    Platform capability consumida por todos os bounded contexts.
    """
    try:
        profile = await service.create_profile(
            full_name=payload.full_name,
            email=payload.email,
            biological_sex=payload.biological_sex,
            birth_date=payload.birth_date,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return _to_output(profile)


@router.get("/{user_id}", response_model=UserProfileOutput)
def get_profile(
    user_id: UUID,
    service: UserProfileService = Depends(get_service),
):
    profile = service.get_by_id(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil não encontrado")
    return _to_output(profile)


@router.post("/{user_id}/goals", response_model=UserProfileOutput)
async def add_health_goal(
    user_id: UUID,
    payload: AddGoalInput,
    service: UserProfileService = Depends(get_service),
):
    try:
        profile = await service.add_health_goal(user_id, payload.goal)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return _to_output(profile)


@router.post("/{user_id}/conditions", response_model=UserProfileOutput)
async def add_health_condition(
    user_id: UUID,
    payload: AddConditionInput,
    service: UserProfileService = Depends(get_service),
):
    try:
        profile = await service.add_health_condition(
            user_id, payload.condition_name, payload.is_chronic
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return _to_output(profile)


def _to_output(profile) -> UserProfileOutput:
    return UserProfileOutput(
        id=str(profile.id),
        full_name=profile.full_name,
        email=profile.email,
        biological_sex=profile.biological_sex.value,
        birth_date=profile.birth_date,
        age=profile.age.years,
        age_group=profile.age.age_group,
        health_goals=[g.value for g in profile.health_goals],
        health_conditions=[
            HealthConditionOutput(name=c.name, is_chronic=c.is_chronic)
            for c in profile.health_conditions
        ],
        is_active=profile.is_active,
    )