"""
AOEN FASE 4 — ISOLAMENTO DE CUSTO

Calcula e registra o custo de cada operação por tenant.
Desacoplado: recebe primitivos, retorna primitivos — sem dependência de ORM.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class CostEvent:
    tenant_id: str
    operation: str
    units: int
    cost_credits: float
    metadata: dict
    recorded_at: datetime


def compute_cost(operation: str, units: int, rate_map: dict[str, float]) -> float:
    rate = rate_map.get(operation, 0.0)
    return round(rate * units, 4)


def build_cost_event(
    tenant_id: str,
    operation: str,
    units: int,
    rate_map: dict[str, float],
    metadata: dict | None = None,
) -> CostEvent:
    return CostEvent(
        tenant_id=tenant_id,
        operation=operation,
        units=units,
        cost_credits=compute_cost(operation, units, rate_map),
        metadata=metadata or {},
        recorded_at=datetime.utcnow(),
    )