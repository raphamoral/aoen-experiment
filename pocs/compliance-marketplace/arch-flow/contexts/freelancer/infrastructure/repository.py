from typing import Dict, List, Optional

from shared.kernel.repository import Repository
from ..domain.entities import FreelancerProfile, FreelancerStatus


class FreelancerRepository(Repository[FreelancerProfile]):
    """
    Repositório em memória para FreelancerProfile.

    Em produção: PostgreSQL com SQLAlchemy async + índice em specializations.code
    para suportar queries de matching eficientes.
    """

    def __init__(self) -> None:
        self._store: Dict[str, FreelancerProfile] = {}

    async def find_by_id(self, id: str) -> Optional[FreelancerProfile]:
        return self._store.get(id)

    async def save(self, aggregate: FreelancerProfile) -> None:
        self._store[aggregate.id] = aggregate

    async def find_by_status(self, status: str) -> List[FreelancerProfile]:
        return [f for f in self._store.values() if f.status.value == status]

    async def find_by_specialization(
        self, code: str
    ) -> List[FreelancerProfile]:
        return [
            f
            for f in self._store.values()
            if f.status == FreelancerStatus.ACTIVE
            and any(s.code == code for s in f.specializations)
        ]

    async def find_active_by_jurisdiction(
        self, country_code: str
    ) -> List[FreelancerProfile]:
        return [
            f
            for f in self._store.values()
            if f.status == FreelancerStatus.ACTIVE
            and any(j.country_code == country_code for j in f.jurisdictions)
        ]