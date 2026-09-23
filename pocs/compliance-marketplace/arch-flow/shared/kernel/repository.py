from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


class Repository(ABC, Generic[T]):
    """
    Base Repository — abstração de persistência para Aggregate Roots.
    Isola o domínio de detalhes de infraestrutura.
    """

    @abstractmethod
    async def find_by_id(self, id: str) -> Optional[T]:
        ...

    @abstractmethod
    async def save(self, aggregate: T) -> None:
        ...