from datetime import datetime

from pydantic import BaseModel


class EmitirCertificadoRequest(BaseModel):
    estudante_id: str
    curso_id: str
    nome_estudante: str
    titulo_curso: str
    carga_horaria: int
    nota_final: float


class CertificadoResponse(BaseModel):
    id: str
    estudante_id: str
    curso_id: str
    nome_estudante: str
    titulo_curso: str
    carga_horaria: int
    nota_final: float
    status: str
    emitido_em: datetime
    hash_verificacao: str
    url_verificacao: str