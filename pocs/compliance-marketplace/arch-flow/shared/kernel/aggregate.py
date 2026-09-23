from dataclasses import dataclass, field
from typing import List
from .entity import Entity
from .domain_event import DomainEvent


@dataclass
class AggregateRoot(Entity):
    """
    Aggregate Root — ponto de entrada e guardião de invariantes do agregado.
    Coleta Domain Events para publicação após persistência.
    """
    _domain_events: List[DomainEvent] = field(
        default_factory=list, init=False, repr=False
    )

    def add_domain_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def collect_domain_events(self) -> List[DomainEvent]:
        events = list(self._domain_events)
        self._domain_events.clear()
        return events