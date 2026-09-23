from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from entities.issuer import Issuer


class IssuerRepository(ABC):

    @abstractmethod
    def save(self, issuer: Issuer) -> Issuer: ...

    @abstractmethod
    def find_by_id(self, issuer_id: UUID) -> Optional[Issuer]: ...

    @abstractmethod
    def find_by_document(self, document: str) -> Optional[Issuer]: ...