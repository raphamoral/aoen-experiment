import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict


@dataclass
class EventoDeDominio:
    """
    Evento de domínio base — fato imutável que ocorreu no sistema.
    Shared Kernel: contrato de integração entre bounded contexts.
    Wardley do barramento: Custom (in-memory) → Commodity (Kafka/RabbitMQ) ao escalar.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    ocorreu_em: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadados: Dict[str, Any] = field(default_factory=dict)

    @property
    def nome(self) -> str:
        return self.__class__.__name__


@dataclass
class MatriculaConcluidaEvento(EventoDeDominio):
    """Publicado quando estudante conclui todas as aulas de um curso."""
    estudante_id: str = ""
    curso_id: str = ""
    matricula_id: str = ""


@dataclass
class AvaliacaoAprovadaEvento(EventoDeDominio):
    """Publicado quando estudante atinge nota mínima na avaliação final."""
    estudante_id: str = ""
    curso_id: str = ""
    tentativa_id: str = ""
    nota: float = 0.0


@dataclass
class CertificadoEmitidoEvento(EventoDeDominio):
    """Publicado após emissão de certificado digital — gatilho para notificações."""
    estudante_id: str = ""
    curso_id: str = ""
    certificado_id: str = ""
    hash_verificacao: str = ""