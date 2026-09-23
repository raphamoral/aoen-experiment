from dataclasses import dataclass, field
from uuid import UUID

from shared.kernel.domain_event import DomainEvent


@dataclass(frozen=True)
class UserProfileCreated(DomainEvent):
    """Evento: Perfil de Usuário Criado.

    Publicado no cadastro inicial do usuário.
    Ponto de entrada do fluxo de valor completo.
    """

    user_id: UUID = field(default=None)
    email: str = field(default="")


@dataclass(frozen=True)
class HealthGoalUpdated(DomainEvent):
    """Evento: Meta de Saúde Atualizada.

    Subscrito por:
      - nutrition: pode ajustar distribuição de macronutrientes
      - ai_analysis: refina o contexto dos próximos insights
    """

    user_id: UUID = field(default=None)
    goal: str = field(default="")