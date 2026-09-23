from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass(frozen=True)
class DomainEvent:
    """Evento de Domínio — fato imutável que ocorreu no domínio.

    Eventos cruzam fronteiras de bounded contexts via event bus,
    permitindo integração assíncrona sem acoplamento direto entre contexts.
    São imutáveis por design: representam algo que JÁ aconteceu.
    """

    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def event_type(self) -> str:
        return self.__class__.__name__