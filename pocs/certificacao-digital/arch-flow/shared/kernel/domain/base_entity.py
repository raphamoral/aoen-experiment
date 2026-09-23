import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Entity:
    """
    Entidade base do domínio.
    Identidade por UUID — independente de persistência (não gerado pelo banco).
    Shared Kernel: utilizado por todos os bounded contexts.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    criado_em: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    atualizado_em: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def tocar(self) -> None:
        """Atualiza timestamp de modificação. Linguagem ubíqua: 'tocar' = registrar alteração."""
        self.atualizado_em = datetime.now(timezone.utc)