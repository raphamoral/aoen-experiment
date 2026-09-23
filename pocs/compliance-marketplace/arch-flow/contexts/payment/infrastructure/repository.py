from typing import Dict, Optional

from shared.kernel.repository import Repository
from ..domain.entities import Payment


class PaymentRepository(Repository[Payment]):
    """Repositório para Payment (em memória)."""

    def __init__(self) -> None:
        self._store: Dict[str, Payment] = {}
        self._by_contract: Dict[str, str] = {}   # contract_id → payment_id

    async def find_by_id(self, id: str) -> Optional[Payment]:
        return self._store.get(id)

    async def save(self, aggregate: Payment) -> None:
        self._store[aggregate.id] = aggregate
        self._by_contract[aggregate.contract_id] = aggregate.id

    async def find_by_contract(self, contract_id: str) -> Optional[Payment]:
        payment_id = self._by_contract.get(contract_id)
        return self._store.get(payment_id) if payment_id else None