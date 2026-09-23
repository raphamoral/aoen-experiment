from dataclasses import dataclass, field
from typing import List

from shared.kernel.domain_event import DomainEvent
from shared.kernel.entity import Entity


@dataclass
class AggregateRoot(Entity):
    """Raiz de Agregado — ponto único de entrada para modificações do agregado.

    Garante consistência transacional dentro das fronteiras do agregado.
    Coleta eventos de domínio para publicação APÓS persistência bem-sucedida,
    garantindo que eventos reflitam apenas mudanças efetivamente persistidas.
    """

    _domain_events: List[DomainEvent] = field(
        default_factory=list, init=False, repr=False
    )

    def record_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def pull_domain_events(self) -> List[DomainEvent]:
        events = list(self._domain_events)
        self._domain_events.clear()
        return events