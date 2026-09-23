from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import Session

from shared.kernel.infrastructure.database import Base
from ..domain.models import Certificado, StatusCertificado
from ..domain.repositories import RepositorioDeCertificado


class CertificadoORM(Base):
    __tablename__ = "certificados"
    id = Column(String, primary_key=True)
    estudante_id = Column(String, nullable=False, index=True)
    curso_id = Column(String, nullable=False)
    nome_estudante = Column(String, nullable=False)
    titulo_curso = Column(String, nullable=False)
    carga_horaria = Column(Integer, nullable=False, default=0)
    nota_final = Column(Float, nullable=False)
    status = Column(String, nullable=False, default="valido")
    emitido_em = Column(String, nullable=False)
    hash_verificacao = Column(String, nullable=False, unique=True, index=True)
    motivo_revogacao = Column(String, nullable=True)


class RepositorioDeCertificadoSQLite(RepositorioDeCertificado):
    def __init__(self, db: Session):
        self._db = db

    def salvar(self, certificado: Certificado) -> Certificado:
        orm = self._db.query(CertificadoORM).filter_by(id=certificado.id).first()
        if orm:
            orm.status = certificado.status.value
            orm.motivo_revogacao = certificado.motivo_revogacao
        else:
            orm = CertificadoORM(
                id=certificado.id,
                estudante_id=certificado.estudante_id,
                curso_id=certificado.curso_id,
                nome_estudante=certificado.nome_estudante,
                titulo_curso=certificado.titulo_curso,
                carga_horaria=certificado.carga_horaria,
                nota_final=certificado.nota_final,
                status=certificado.status.value,
                emitido_em=certificado.emitido_em.isoformat(),
                hash_verificacao=certificado.hash_verificacao,
            )
            self._db.add(orm)
        self._db.commit()
        self._db.refresh(orm)
        return self._para_dominio(orm)

    def buscar_por_id(self, certificado_id: str) -> Optional[Certificado]:
        orm = self._db.query(CertificadoORM).filter_by(id=certificado_id).first()
        return self._para_dominio(orm) if orm else None

    def buscar_por_hash(self, hash_verificacao: str) -> Optional[Certificado]:
        orm = self._db.query(CertificadoORM).filter_by(hash_verificacao=hash_verificacao).first()
        return self._para_dominio(orm) if orm else None

    def listar_por_estudante(self, estudante_id: str) -> List[Certificado]:
        return [self._para_dominio(o) for o in
                self._db.query(CertificadoORM).filter_by(estudante_id=estudante_id).all()]

    @staticmethod
    def _para_dominio(orm: CertificadoORM) -> Certificado:
        return Certificado(
            id=orm.id,
            estudante_id=orm.estudante_id,
            curso_id=orm.curso_id,
            nome_estudante=orm.nome_estudante,
            titulo_curso=orm.titulo_curso,
            carga_horaria=orm.carga_horaria,
            nota_final=orm.nota_final,
            status=StatusCertificado(orm.status),
            emitido_em=datetime.fromisoformat(orm.emitido_em),
            hash_verificacao=orm.hash_verificacao,
            motivo_revogacao=orm.motivo_revogacao,
        )