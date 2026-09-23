from dataclasses import dataclass, field
from uuid import UUID

from shared.kernel.domain_event import DomainEvent


@dataclass(frozen=True)
class AnalysisGenerated(DomainEvent):
    """Evento: Análise de IA Gerada.

    Publicado quando a análise personalizada está completa.
    Subscrito por:
      - nutrition: refinamento do plano com base nos insights
      - user_profile: registro no histórico clínico
    """

    analysis_id: UUID = field(default=None)
    user_id: UUID = field(default=None)
    lab_result_id: UUID = field(default=None)
    insight_count: int = field(default=0)
    has_critical: bool = field(default=False)


@dataclass(frozen=True)
class CriticalInsightFound(DomainEvent):
    """Evento: Insight Crítico Identificado.

    Publicado imediatamente quando risco grave é detectado.
    Deve acionar notificação prioritária ao usuário e,
    futuramente, alerta para profissional de saúde vinculado.
    """

    analysis_id: UUID = field(default=None)
    user_id: UUID = field(default=None)
    insight_title: str = field(default="")
    risk_level: str = field(default="critico")