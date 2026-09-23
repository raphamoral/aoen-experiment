import asyncio
from collections import defaultdict
from typing import Callable, Dict, List, Type
from shared.kernel.domain_event import DomainEvent


class DomainEventBus:
    """
    Event Bus — desacopla produtores e consumidores de Domain Events.
    Permite que bounded contexts reajam a eventos de outros contextos
    sem acoplamento direto (comunicação assíncrona entre times/contextos).
    """

    def __init__(self) -> None:
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)

    def subscribe(self, event_type: Type[DomainEvent], handler: Callable) -> None:
        self._handlers[event_type.__name__].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        handlers = self._handlers.get(event.__class__.__name__, [])
        await asyncio.gather(*[handler(event) for handler in handlers])


# Singleton global — em produção substituir por broker assíncrono (RabbitMQ, Kafka)
event_bus = DomainEventBus()