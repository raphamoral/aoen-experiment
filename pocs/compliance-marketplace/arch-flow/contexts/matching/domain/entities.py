from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

from shared.kernel.aggregate import AggregateRoot
from .value_objects import MatchScore, ProjectRequirement


class MatchStatus(str, Enum):
    PENDING = "pending"     # Calculado, aguardando aceite do cliente
    ACCEPTED = "accepted"   # Cliente aceito — inicia negociação de contrato
    REJECTED = "rejected"   # Cliente rejeitou o match
    EXPIRED = "expired"     # Expirado sem resposta


@dataclass
class MatchResult(AggregateRoot):
    """
    MatchResult — resultado do algoritmo de matching compliance-especializado.

    Maturidade Wardley: GENESIS
    Representa a proposta de conexão entre cliente e freelancer,
    gerada pelo algoritmo proprietário de matching.
    """
    client_id: str = ""
    project_requirement: Optional[ProjectRequirement] = None
    freelancer_id: str = ""
    score: Optional[MatchScore] = None
    status: MatchStatus = MatchStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)

    def accept(self) -> None:
        if self.status != MatchStatus.PENDING:
            raise ValueError("Apenas matches pendentes podem ser aceitos")
        self.status = MatchStatus.ACCEPTED

    def reject(self) -> None:
        if self.status != MatchStatus.PENDING:
            raise ValueError("Apenas matches pendentes podem ser rejeitados")
        self.status = MatchStatus.REJECTED

    def expire(self) -> None:
        self.status = MatchStatus.EXPIRED