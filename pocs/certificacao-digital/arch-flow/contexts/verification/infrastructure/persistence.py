import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import Session

from shared.kernel.infrastructure.database import Base
from ..domain.repositories import RepositorioDeVerificacao


class RegistroVerificacaoORM(Base):
    __tablename__ = "registros_verificacao"
    id = Column(String, primary_key=True)
    hash_verificacao = Column(String, nullable=False, index=True)
    ip_solicitante = Column(String, nullable=False)
    resultado = Column(Boolean, nullable=False)
    consultado_em = Column(String, nullable=False)


class RepositorioDeVerificacaoSQLite(RepositorioDeVerificacao):
    """
    Monolito modular: lê diretamente a tabela do contexto Certificação como read model.
    Decisão consciente de trade-off: simplicidade MVP vs. acoplamento de banco.
    Plano de migração: substituir por chamada HTTP ao endpoint interno de Certificação
    quando os contextos forem separados em serviços independentes.
    """

    def __init__(self, db: Session):
        self._db = db

    def buscar_por_hash(self, hash_verificacao: str) -> Optional[Dict[str, Any]]:
        from contexts.certification.infrastructure.persistence import CertificadoORM
        orm = self._db.query(CertificadoORM).filter_by(hash_verificacao=hash_verificacao).first()
        if not orm:
            return None
        return {
            "id": orm.id,
            "nome_estudante": orm.nome_estudante,
            "titulo_curso": orm.titulo_curso,
            "carga_horaria": orm.carga_horaria,
            "nota_final": orm.nota_final,
            "emitido_em": datetime.fromisoformat(orm.emitido_em),
            "status": orm.status,
            "hash_verificacao": orm.hash_verificacao,
        }

    def registrar_auditoria(self, hash_verificacao: str, ip_solicitante: str, resultado: bool) -> None:
        registro = RegistroVerificacaoORM(
            id=str(uuid.uuid4()),
            hash_verificacao=hash_verificacao,
            ip_solicitante=ip_solicitante,
            resultado=resultado,
            consultado_em=datetime.utcnow().isoformat(),
        )
        self._db.add(registro)
        self._db.commit()