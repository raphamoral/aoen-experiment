from typing import Dict, List, Optional

from shared.kernel.repository import Repository
from ..domain.entities import Contract


class ContractRepository(Repository[Contract]):
    """
    Repositório para Contract (em memória).

    Em produção: PostgreSQL. Considerar event sourcing para auditoria
    completa do ciclo de vida contratual (requisito em compliance financeiro).
    """

    def __init__(self) -> None:
        self._store: Dict[str, Contract] = {}

    async def find_by_id(self, id: str) -> Optional[Contract]:
        return self._store.get(id)

    async def save(self, aggregate: Contract) -> None:
        self._store[aggregate.id] = aggregate

    async def find_by_client(self, client_id: str) -> List[Contract]:
        return [c for c in self._store.values() if c.client_id == client_id]

    async def find_by_freelancer(self, freelancer_id: str) -> List[Contract]:
        return [c for c in self._store.values() if c.freelancer_id == freelancer_id]

    async def find_by_match(self, match_id: str) -> Optional[Contract]:
        return next(
            (c for c in self._store.values() if c.match_id == match_id), None
        )