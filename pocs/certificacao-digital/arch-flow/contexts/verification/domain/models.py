from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from shared.kernel.domain.base_entity import Entity


@dataclass
class ResultadoVerificacao:
    """
    Read model para verificação pública de certificados.
    Contexto separado para isolar visibilidade pública do domínio interno de Certificação.
    Contém apenas o que um verificador externo precisa saber — nunca IDs internos.
    Wardley: Custom — interface de confiança pública é diferencial do produto.
    """
    valido: bool
    hash_verificacao: str
    nome_estudante: Optional[str] = None
    titulo_curso: Optional[str] = None
    carga_horaria: Optional[int] = None
    nota_final: Optional[float] = None
    emitido_em: Optional[datetime] = None
    status: Optional[str] = None
    mensagem: str = ""
    verificado_em: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RegistroDeVerificacao(Entity):
    """
    Auditoria de consultas públicas de verificação.
    Permite detectar scraping massivo e gerar métricas de confiança do sistema.
    """
    hash_verificacao: str = ""
    ip_solicitante: str = ""
    resultado: bool = False
    consultado_em: datetime = field(default_factory=lambda: datetime.now(timezone.utc))