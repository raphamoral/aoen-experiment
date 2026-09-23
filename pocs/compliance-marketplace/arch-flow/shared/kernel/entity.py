import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Entity:
    """Base Entity — possui identidade única que persiste no tempo."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)