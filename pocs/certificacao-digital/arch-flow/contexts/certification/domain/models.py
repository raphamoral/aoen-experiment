import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from shared.kernel.domain.base_entity import Entity
from shared.kernel.domain.value_objects import HashDeVerificacao


class StatusCertificado(str, Enum):
    VALIDO = "valido"
    REVOGADO = "revogado"


def _gerar_hash_verificacao() -> str:
    """
    Gera identificador público único para verificação.
    token aleatório + timestamp → SHA-256 (truncado) = 32 hex chars.
    Wardley: Custom → Genesis (evolução planejada para W3C Verifiable Credentials).
    """
    token = secrets.token_hex(16)
    timestamp = str(datetime.now(timezone.utc).timestamp())
    return hashlib.sha256(f"{token}{timestamp}".encode()).hexdigest()[:32]


@dataclass
class Certificado(Entity):
    """
    Agregado raiz do contexto Certificação.
    Credencial digital imutável após emissão — só pode ser revogada, nunca alterada.
    Invariante: uma vez emitido, o conteúdo (nome, curso, nota) é imutável.
    """
    estudante_id: str = ""
    curso_id: str = ""
    nome_estudante: str = ""
    titulo_curso: str = ""
    carga_horaria: int = 0
    nota_final: float = 0.0
    status: StatusCertificado = StatusCertificado.VALIDO
    emitido_em: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    hash_verificacao: str = field(default_factory=_gerar_hash_verificacao)
    motivo_revogacao: Optional[str] = None

    def revogar(self, motivo: str) -> None:
        if self.status == StatusCertificado.REVOGADO:
            raise ValueError("Certificado já foi revogado.")
        self.status = StatusCertificado.REVOGADO
        self.motivo_revogacao = motivo
        self.tocar()

    @property
    def esta_valido(self) -> bool:
        return self.status == StatusCertificado.VALIDO

    @property
    def hash_de_verificacao(self) -> HashDeVerificacao:
        return HashDeVerificacao(self.hash_verificacao)