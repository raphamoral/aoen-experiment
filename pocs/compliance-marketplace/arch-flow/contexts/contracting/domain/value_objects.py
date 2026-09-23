from dataclasses import dataclass
from datetime import datetime
from shared.kernel.value_object import ValueObject


@dataclass(frozen=True)
class ContractValue(ValueObject):
    """Valor financeiro total do contrato."""
    amount: float
    currency: str = "BRL"

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise ValueError("Valor do contrato deve ser positivo")


@dataclass(frozen=True)
class DeliverableScope(ValueObject):
    """
    Escopo de entregável do projeto de compliance.

    Linguagem ubíqua:
    - Entregável = produto concreto e mensurável do trabalho regulatório
    - Ex: "Mapeamento de dados LGPD", "Política de PLD-FT", "Relatório de GAP CVM"
    """
    title: str
    description: str
    estimated_hours: int
    framework_code: str   # Framework regulatório alvo do entregável


@dataclass(frozen=True)
class ContractPeriod(ValueObject):
    """Período de vigência do contrato."""
    start_date: datetime
    end_date: datetime

    def __post_init__(self) -> None:
        if self.end_date <= self.start_date:
            raise ValueError("Data de término deve ser posterior ao início")

    @property
    def duration_days(self) -> int:
        return (self.end_date - self.start_date).days