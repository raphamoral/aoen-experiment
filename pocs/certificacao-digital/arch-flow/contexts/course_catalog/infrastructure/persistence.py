from typing import List, Optional

from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import Session

from shared.kernel.infrastructure.database import Base
from ..domain.models import Curso, Instrutor, MaturidadeCurso, StatusCurso
from ..domain.repositories import RepositorioDeCurso, RepositorioDeInstrutor


class InstrutorORM(Base):
    __tablename__ = "instrutores"
    id = Column(String, primary_key=True)
    nome = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    especialidade = Column(String, nullable=False)


class CursoORM(Base):
    __tablename__ = "cursos"
    id = Column(String, primary_key=True)
    titulo = Column(String, nullable=False)
    descricao = Column(String, nullable=False)
    carga_horaria = Column(Integer, nullable=False)
    maturidade = Column(String, nullable=False, default="custom")
    status = Column(String, nullable=False, default="rascunho")
    instrutor_id = Column(String, nullable=False)
    nota_minima_aprovacao = Column(Float, nullable=False, default=7.0)


class RepositorioDeCursoSQLite(RepositorioDeCurso):
    def __init__(self, db: Session):
        self._db = db

    def salvar(self, curso: Curso) -> Curso:
        orm = self._db.query(CursoORM).filter_by(id=curso.id).first()
        if orm:
            orm.titulo = curso.titulo
            orm.descricao = curso.descricao
            orm.carga_horaria = curso.carga_horaria
            orm.maturidade = curso.maturidade.value
            orm.status = curso.status.value
            orm.instrutor_id = curso.instrutor_id
            orm.nota_minima_aprovacao = curso.nota_minima_aprovacao
        else:
            orm = CursoORM(
                id=curso.id,
                titulo=curso.titulo,
                descricao=curso.descricao,
                carga_horaria=curso.carga_horaria,
                maturidade=curso.maturidade.value,
                status=curso.status.value,
                instrutor_id=curso.instrutor_id,
                nota_minima_aprovacao=curso.nota_minima_aprovacao,
            )
            self._db.add(orm)
        self._db.commit()
        self._db.refresh(orm)
        return self._para_dominio(orm)

    def buscar_por_id(self, curso_id: str) -> Optional[Curso]:
        orm = self._db.query(CursoORM).filter_by(id=curso_id).first()
        return self._para_dominio(orm) if orm else None

    def listar_publicados(self) -> List[Curso]:
        return [self._para_dominio(o) for o in self._db.query(CursoORM).filter_by(status="publicado").all()]

    def listar_todos(self) -> List[Curso]:
        return [self._para_dominio(o) for o in self._db.query(CursoORM).all()]

    @staticmethod
    def _para_dominio(orm: CursoORM) -> Curso:
        return Curso(
            id=orm.id,
            titulo=orm.titulo,
            descricao=orm.descricao,
            carga_horaria=orm.carga_horaria,
            maturidade=MaturidadeCurso(orm.maturidade),
            status=StatusCurso(orm.status),
            instrutor_id=orm.instrutor_id,
            nota_minima_aprovacao=orm.nota_minima_aprovacao,
        )


class RepositorioDeInstrutorSQLite(RepositorioDeInstrutor):
    def __init__(self, db: Session):
        self._db = db

    def salvar(self, instrutor: Instrutor) -> Instrutor:
        orm = InstrutorORM(
            id=instrutor.id, nome=instrutor.nome,
            email=instrutor.email, especialidade=instrutor.especialidade,
        )
        self._db.merge(orm)
        self._db.commit()
        return instrutor

    def buscar_por_id(self, instrutor_id: str) -> Optional[Instrutor]:
        orm = self._db.query(InstrutorORM).filter_by(id=instrutor_id).first()
        if not orm:
            return None
        return Instrutor(id=orm.id, nome=orm.nome, email=orm.email, especialidade=orm.especialidade)