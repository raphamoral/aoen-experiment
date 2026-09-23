from dataclasses import dataclass, field
from datetime import date
from uuid import UUID

from shared.kernel.domain_event import DomainEvent


@dataclass(frozen=True)
class LabResultReceived(DomainEvent):
    """Evento: Resultado Laboratorial Recebido.

    Publicado quando um novo exame é cadastrado no sistema.
    Subscrito por:
      - ai_analysis: inicia análise personalizada automaticamente
    """

    lab_result_id: UUID = field(default=None)
    user_id: UUID = field(default=None)
    collection_date: date = field(default=None)


@dataclass(frozen=True)
class BiomarkerOutOfRange(DomainEvent):
    """Evento: Biomarcador Fora da Faixa de Referência.

    Publicado para cada biomarcador alterado identificado no exame.
    Subscrito por:
      - nutrition: ajuste terapêutico do plano alimentar
      - ai_analysis: priorização de insights críticos
    """

    lab_result_id: UUID = field(default=None)
    user_id: UUID = field(default=None)
    biomarker_name: str = field(default="")
    value: float = field(default=0.0)
    status: str = field(default="alterado")