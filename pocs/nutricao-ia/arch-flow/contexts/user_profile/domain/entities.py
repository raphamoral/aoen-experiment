from dataclasses import dataclass, field
from datetime import date
from typing import List
from uuid import UUID

from shared.kernel.aggregate_root import AggregateRoot
from contexts.user_profile.domain.value_objects import (
    Age,
    BiologicalSex,
    HealthCondition,
    HealthGoal,
)
from contexts.user_profile.domain.events import HealthGoalUpdated, UserProfileCreated


@dataclass
class UserProfile(AggregateRoot):
    """Perfil do Usuário — agregado raiz do contexto de perfil.

    Centraliza dados pessoais e clínicos que contextualizam as análises.
    Fornece o método to_ai_context() que traduz o perfil para o formato
    consumido pelo contexto de AI Analysis (evita acoplamento direto).

    Wardley: Product → Commodity.
    Autenticação e perfil são maduros; o diferencial não está aqui,
    mas em como o perfil enriquece a análise de IA.

    Team Topologies: Platform Team.
    Fornece capacidades compartilhadas para laboratory, nutrition e
    ai_analysis sem criar dependência entre os stream-aligned teams.
    """

    full_name: str
    email: str
    biological_sex: BiologicalSex
    birth_date: date
    health_goals: List[HealthGoal] = field(default_factory=list)
    health_conditions: List[HealthCondition] = field(default_factory=list)
    is_active: bool = True

    @classmethod
    def create(
        cls,
        full_name: str,
        email: str,
        biological_sex: BiologicalSex,
        birth_date: date,
    ) -> "UserProfile":
        profile = cls(
            full_name=full_name,
            email=email,
            biological_sex=biological_sex,
            birth_date=birth_date,
        )
        profile.record_event(
            UserProfileCreated(user_id=profile.id, email=email)
        )
        return profile

    @property
    def age(self) -> Age:
        today = date.today()
        years = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            years -= 1
        return Age(years=years)

    def add_health_goal(self, goal: HealthGoal) -> None:
        if goal not in self.health_goals:
            self.health_goals.append(goal)
            self.record_event(
                HealthGoalUpdated(user_id=self.id, goal=goal.value)
            )

    def add_health_condition(self, condition: HealthCondition) -> None:
        self.health_conditions.append(condition)

    def deactivate(self) -> None:
        self.is_active = False

    def to_ai_context(self) -> dict:
        """Traduz o perfil para o contrato esperado pelo contexto de IA.

        Camada de tradução entre contexts: evita que o ai_analysis
        dependa do modelo de domínio do user_profile diretamente.
        """
        return {
            "age": self.age.years,
            "biological_sex": self.biological_sex.value,
            "health_goals": [g.value for g in self.health_goals],
            "health_conditions": [c.name for c in self.health_conditions],
        }