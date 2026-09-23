from typing import List, Optional

from sqlalchemy import Boolean, Column, Float, ForeignKey, String
from sqlalchemy.orm import Session, relationship

from shared.kernel.infrastructure.database import Base
from ..domain.models import Matricula, RegistroDeProgresso, StatusMatricula
from ..domain.repositories import RepositorioDeMatricula


class RegistroDeProgressoORM(Base):
    __tablename__ = "registros_de_progresso"
    id = Column(String, primary_key=True)
    matricula_id = Column(String, ForeignKey("matriculas.id"), nullable=False)
    aula_id = Column(String, nullable=False)
    concluida = Column(Boolean, default=False)
    percentual_assistido = Column(Float, default=0.0)


class MatriculaORM(Base):
    __tablename__ = "matriculas"
    id = Column(String, primary_key=True)
    estudante_id = Column(String, nullable=False)
    curso_id = Column(String, nullable=False)
    status = Column(String, nullable=False, default="ativa")
    registros = relationship("RegistroDeProgressoORM", cascade="all, delete-orphan")


class RepositorioDeMatriculaSQLite(RepositorioDeMatricula):
    def __init__(self, db: Session):
        self._db = db

    def salvar(self, matricula: Matricula) -> Matricula:
        orm = self._db.query(MatriculaORM).filter_by(id=matricula.id).first()
        if orm:
            orm.status = matricula.status.value
            ids_existentes = {r.id for r in orm.registros}
            for reg in matricula.registros_de_progresso:
                if reg.id in ids_existentes:
                    reg_orm = next(r for r in orm.registros if r.id == reg.id)
                    reg_orm.concluida = reg.concluida
                    reg_orm.percentual_assistido = reg.percentual_assistido
                else:
                    orm.registros.append(RegistroDeProgressoORM(
                        id=reg.id, matricula_id=matricula.id,
                        aula_id=reg.aula_id, concluida=reg.concluida,
                        percentual_assistido=reg.percentual_assistido,
                    ))
        else:
            orm = MatriculaORM(
                id=matricula.id,
                estudante_id=matricula.estudante_id,
                curso_id=matricula.curso_id,
                status=matricula.status.value,
                registros=[
                    RegistroDeProgressoORM(
                        id=r.id, matricula_id=matricula.id,
                        aula_id=r.aula_id, concluida=r.concluida,
                        percentual_assistido=r.percentual_assistido,
                    ) for r in matricula.registros_de_progresso
                ],
            )
            self._db.add(orm)
        self._db.commit()
        self._db.refresh(orm)
        return self._para_dominio(orm)

    def buscar_por_id(self, matricula_id: str) -> Optional[Matricula]:
        orm = self._db.query(MatriculaORM).filter_by(id=matricula_id).first()
        return self._para_dominio(orm) if orm else None

    def buscar_por_estudante_e_curso(self, estudante_id: str, curso_id: str) -> Optional[Matricula]:
        orm = self._db.query(MatriculaORM).filter_by(
            estudante_id=estudante_id, curso_id=curso_id
        ).first()
        return self._para_dominio(orm) if orm else None

    def listar_por_estudante(self, estudante_id: str) -> List[Matricula]:
        return [self._para_dominio(o) for o in
                self._db.query(MatriculaORM).filter_by(estudante_id=estudante_id).all()]

    @staticmethod
    def _para_dominio(orm: MatriculaORM) -> Matricula:
        registros = [
            RegistroDeProgresso(
                id=r.id, aula_id=r.aula_id,
                concluida=r.concluida, percentual_assistido=r.percentual_assistido,
            ) for r in orm.registros
        ]
        return Matricula(
            id=orm.id,
            estudante_id=orm.estudante_id,
            curso_id=orm.curso_id,
            status=StatusMatricula(orm.status),
            registros_de_progresso=registros,
        )