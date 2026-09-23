import asyncio
import logging
from collections import defaultdict
from typing import Callable, Dict, List, Type

from shared.kernel.domain_event import DomainEvent

logger = logging.getLogger(__name__)

HandlerFunc = Callable[[DomainEvent], None]


class InMemoryEventBus:
    """Barramento de eventos em memória para integração entre bounded contexts.

    Wardley: Commodity — em produção substitua por Kafka, RabbitMQ ou SNS/SQS
    para desacoplamento temporal real entre contexts (este é apenas para dev).

    Pattern: Observer / Pub-Sub assíncrono.
    Contexts publicam fatos; outros contexts reagem sem conhecer a fonte.
    """

    def __init__(self) -> None:
        self._handlers: Dict[str, List[HandlerFunc]] = defaultdict(list)

    def subscribe(self, event_type: Type[DomainEvent], handler: HandlerFunc) -> None:
        self._handlers[event_type.__name__].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception:
                logger.exception(
                    "Erro no handler de evento %s", event.event_type
                )


event_bus = InMemoryEventBus()