from typing import Dict, List, Optional

from shared.kernel.repository import Repository
from ..domain.entities import RegulatoryFramework


class RegulatoryFrameworkRepository(Repository[RegulatoryFramework]):
    """
    Repositório para RegulatoryFramework (em memória).

    Em produção: PostgreSQL com full-text search para busca semântica
    nos textos regulatórios (extensão pg_trgm ou Elasticsearch).
    """

    def __init__(self) -> None:
        self._store: Dict[str, RegulatoryFramework] = {}
        self._by_code: Dict[str, str] = {}   # code → id

    async def find_by_id(self, id: str) -> Optional[RegulatoryFramework]:
        return self._store.get(id)

    async def save(self, aggregate: RegulatoryFramework) -> None:
        self._store[aggregate.id] = aggregate
        self._by_code[aggregate.code] = aggregate.id

    async def find_by_code(self, code: str) -> Optional[RegulatoryFramework]:
        framework_id = self._by_code.get(code)
        return self._store.get(framework_id) if framework_id else None

    async def find_by_category(self, category_code: str) -> List[RegulatoryFramework]:
        return [
            f
            for f in self._store.values()
            if f.category and f.category.code == category_code and f.is_active
        ]

    async def find_all_active(self) -> List[RegulatoryFramework]:
        return [f for f in self._store.values() if f.is_active]