from dataclasses import dataclass, field
from uuid import UUID

from shared.kernel.domain_event import DomainEvent


@dataclass(frozen=True)
class NutritionalPlanCreated(DomainEvent):
    """Evento: Plano Nutricional Criado.

    Publicado quando um novo plano é gerado a partir de exames.
    Subscrito por:
      - user_profile: atualização do histórico clínico do usuário
    """

    plan_id: UUID = field(default=None)
    user_id: UUID = field(default=None)
    lab_result_id: UUID = field(default=None)


@dataclass(frozen=True)
class DeficiencyIdentified(DomainEvent):
    """Evento: Deficiência Nutricional Identificada.

    Publicado quando nutriente de alta prioridade terapêutica é detectado.
    Subscrito por:
      - ai_analysis: enriquecimento dos insights clínicos gerados
    """

    plan_id: UUID = field(default=None)
    user_id: UUID = field(default=None)
    nutrient_name: str = field(default="")
    priority: str = field(default="alta")