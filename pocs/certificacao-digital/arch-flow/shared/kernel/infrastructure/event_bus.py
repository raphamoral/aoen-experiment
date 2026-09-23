import logging
from typing import Callable, Dict, List, Type

from shared.kernel.domain.events import EventoDeDominio

logger = logging.getLogger(__name__)


class BarramentoDeEventos:
    """
    Barramento de eventos in-memory.
    Wardley: Custom — suficiente para monolito modular.
    Plano de evolução: substituir por implementação Kafka/RabbitMQ sem alterar interfaces
    dos contextos (os handlers permanecem iguais; só muda a infraestrutura de entrega).
    Team Topology: Plataforma interna fornecida pelo Platform Team.
    """
    _handlers: Dict[str, List[Callable]] = {}

    @classmethod
    def assinar(cls, tipo_evento: Type[EventoDeDominio], handler: Callable) -> None:
        nome = tipo_evento.__name__
        if nome not in cls._handlers:
            cls._handlers[nome] = []
        cls._handlers[nome].append(handler)
        logger.info(f"Handler registrado: {nome}")

    @classmethod
    async def publicar(cls, evento: EventoDeDominio) -> None:
        nome = evento.__class__.__name__
        handlers = cls._handlers.get(nome, [])
        logger.info(f"Evento publicado: {nome} (id={evento.id})")
        for handler in handlers:
            try:
                await handler(evento)
            except Exception as exc:
                logger.error(f"Falha no handler de {nome}: {exc}")

    @classmethod
    def limpar(cls) -> None:
        """Limpa handlers — útil em testes."""
        cls._handlers.clear()