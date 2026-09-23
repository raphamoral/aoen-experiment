from typing import List, Optional
from uuid import UUID

from sqlalchemy import Boolean, Column, Date, JSON, String
from sqlalchemy.orm import Session

from shared.infra.database import Base
from contexts.user_profile.domain.entities import UserProfile
from contexts.user_profile.domain.value_objects import (
    BiologicalSex,
    HealthCondition,
    HealthGoal,
)


class UserProfileModel(Base):
    __tablename__ = "user_profiles"

    id = Column(String(36), primary_key=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    biological_sex = Column(String(20), nullable=False)
    birth_date = Column(Date, nullable=False)
    health_goals_json = Column(JSON, nullable=False, default=list)
    health_conditions_json = Column(JSON, nullable=False, default=list)
    is_active = Column(Boolean, default=True)


class UserProfileRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, profile: UserProfile) -> None:
        model = UserProfileModel(
            id=str(profile.id),
            full_name=profile.full_name,
            email=profile.email,
            biological_sex=profile.biological_sex.value,
            birth_date=profile.birth_date,
            health_goals_json=[g.value for g in profile.health_goals],
            health_conditions_json=[
                {
                    "name": c.name,
                    "is_chronic": c.is_chronic,
                    "affects_nutrition": c.affects_nutrition,
                }
                for c in profile.health_conditions
            ],
            is_active=profile.is_active,
        )
        self._session.merge(model)
        self._session.commit()

    def find_by_id(self, user_id: UUID) -> Optional[UserProfile]:
        model = (
            self._session.query(UserProfileModel)
            .filter_by(id=str(user_id))
            .first()
        )
        return self._to_domain(model) if model else None

    def find_by_email(self, email: str) -> Optional[UserProfile]:
        model = (
            self._session.query(UserProfileModel).filter_by(email=email).first()
        )
        return self._to_domain(model) if model else None

    def _to_domain(self, model: UserProfileModel) -> UserProfile:
        from uuid import UUID as _UUID

        profile = UserProfile(
            id=_UUID(model.id),
            full_name=model.full_name,
            email=model.email,
            biological_sex=BiologicalSex(model.biological_sex),
            birth_date=model.birth_date,
            is_active=model.is_active,
        )
        for goal_val in model.health_goals_json or []:
            try:
                profile.health_goals.append(HealthGoal(goal_val))
            except ValueError:
                pass
        for c_data in model.health_conditions_json or []:
            profile.health_conditions.append(
                HealthCondition(
                    name=c_data["name"],
                    is_chronic=c_data.get("is_chronic", False),
                    affects_nutrition=c_data.get("affects_nutrition", True),
                )
            )
        return profile