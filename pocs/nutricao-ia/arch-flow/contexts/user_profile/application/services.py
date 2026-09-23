import logging
from datetime import date
from typing import List, Optional
from uuid import UUID

from shared.events.event_bus import event_bus
from contexts.user_profile.domain.entities import UserProfile
from contexts.user_profile.domain.value_objects import (
    BiologicalSex,
    HealthCondition,
    HealthGoal,
)
from contexts.user_profile.infrastructure.repository import UserProfileRepository

logger = logging.getLogger(__name__)


class UserProfileService:
    """Serviço de Perfil do Usuário.

    Gerencia o ciclo de vida do perfil e fornece contexto clínico
    para os contexts de análise IA e nutrição.
    Platform capability: consumida por múltiplos stream-aligned teams.
    """

    def __init__(self, repository: UserProfileRepository) -> None:
        self._repo = repository

    async def create_profile(
        self,
        full_name: str,
        email: str,
        biological_sex: str,
        birth_date: date,
    ) -> UserProfile:
        if self._repo.find_by_email(email):
            raise ValueError(f"Usuário com email {email} já cadastrado")

        profile = UserProfile.create(
            full_name=full_name,
            email=email,
            biological_sex=BiologicalSex(biological_sex),
            birth_date=birth_date,
        )
        self._repo.save(profile)

        for event in profile.pull_domain_events():
            await event_bus.publish(event)

        logger.info("Perfil criado: %s (%s)", full_name, email)
        return profile

    def get_by_id(self, user_id: UUID) -> Optional[UserProfile]:
        return self._repo.find_by_id(user_id)

    async def add_health_goal(self, user_id: UUID, goal: str) -> UserProfile:
        profile = self._repo.find_by_id(user_id)
        if not profile:
            raise ValueError("Usuário não encontrado")
        profile.add_health_goal(HealthGoal(goal))
        self._repo.save(profile)
        for event in profile.pull_domain_events():
            await event_bus.publish(event)
        return profile

    async def add_health_condition(
        self,
        user_id: UUID,
        condition_name: str,
        is_chronic: bool = False,
    ) -> UserProfile:
        profile = self._repo.find_by_id(user_id)
        if not profile:
            raise ValueError("Usuário não encontrado")
        profile.add_health_condition(
            HealthCondition(name=condition_name, is_chronic=is_chronic)
        )
        self._repo.save(profile)
        return profile