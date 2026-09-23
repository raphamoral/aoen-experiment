from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class VerificacaoResponse(BaseModel):
    valido: bool
    hash_verificacao: str
    nome_estudante: Optional[str] = None
    titulo_curso: Optional[str] = None
    carga_horaria: Optional[int] = None
    nota_final: Optional[float] = None
    emitido_em: Optional[datetime] = None
    status: Optional[str] = None
    mensagem: str
    verificado_em: datetime