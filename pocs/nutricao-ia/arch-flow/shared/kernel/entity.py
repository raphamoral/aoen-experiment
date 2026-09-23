from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Entity:
    """Entidade — tem identidade única que persiste ao longo do tempo.

    Duas entidades são iguais se tiverem o mesmo ID,
    independentemente dos seus atributos atuais.
    A identidade é o que define uma entidade, não seus dados.
    """

    id: UUID = field(default_factory=uuid4)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)