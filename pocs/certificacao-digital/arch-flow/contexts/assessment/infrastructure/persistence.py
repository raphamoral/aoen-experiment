from typing import Optional

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Session, relationship

from shared.kernel.infrastructure.database import Base
from ..domain.models import (
    Alternativa, Avaliacao, Questao, RespostaQuestao, StatusTentativa, Tentativa, TipoQuestao,
)
from ..domain.repositories import RepositorioDeAvaliacao, RepositorioDeTentativa


class AlternativaORM(Base):
    __tablename__ = "alternativas"
    id = Column(String, primary_key=True)
    questao_id = Column(String, ForeignKey("questoes.id"), nullable=False)
    texto = Column(String, nullable=False)
    correta = Column(Boolean, default=False)


class QuestaoORM(Base):
    __tablename__ = "questoes"
    id = Column(String, primary_key=True)
    avaliacao_id = Column(String, ForeignKey("avaliacoes.id"), nullable=False)
    enunciado = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    peso = Column(Float, default=1.0)
    alternativas = relationship("AlternativaORM", cascade="all, delete-orphan")


class AvaliacaoORM(Base):
    __tablename__ = "avaliacoes"
    id = Column(String, primary_key=True)
    curso_id = Column(String, nullable=False)
    titulo = Column(String, nullable=False)
    nota_minima_aprovacao = Column(Float, default=7.0)
    tentativas_maximas = Column(Integer, default=3)
    questoes = relationship("QuestaoORM", cascade="all, delete-orphan")


class RespostaQuestaoORM(Base):
    __tablename__ = "respostas_questoes"
    id = Column(String, primary_key=True)
    tentativa_id = Column(String, ForeignKey("tentativas.id"), nullable=False)
    questao_id = Column(String, nullable=False)
    alternativa_id = Column(String, nullable=False)


class TentativaORM(Base):
    __tablename__ = "tentativas"
    id = Column(String, primary_key=True)
    avaliacao_id = Column(String, nullable=False)
    estudante_id = Column(String, nullable=False)
    status = Column(String, nullable=False)
    nota = Column(Float, default=0.0)
    respostas = relationship("RespostaQuestaoORM", cascade="all, delete-orphan")


class RepositorioDeAvaliacaoSQLite(RepositorioDeAvaliacao):
    def __init__(self, db: Session):
        self._db = db

    def salvar(self, avaliacao: Avaliacao) -> Avaliacao:
        orm = AvaliacaoORM(
            id=avaliacao.id,
            curso_id=avaliacao.curso_id,
            titulo=avaliacao.titulo,
            nota_minima_aprovacao=avaliacao.nota_minima_aprovacao,
            tentativas_maximas=avaliacao.tentativas_maximas,
            questoes=[
                QuestaoORM(
                    id=q.id, avaliacao_id=avaliacao.id,
                    enunciado=q.enunciado, tipo=q.tipo.value, peso=q.peso,
                    alternativas=[
                        AlternativaORM(id=a.id, questao_id=q.id, texto=a.texto, correta=a.correta)
                        for a in q.alternativas
                    ],
                ) for q in avaliacao.questoes
            ],
        )
        self._db.merge(orm)
        self._db.commit()
        return avaliacao

    def buscar_por_id(self, avaliacao_id: str) -> Optional[Avaliacao]:
        orm = self._db.query(AvaliacaoORM).filter_by(id=avaliacao_id).first()
        return self._para_dominio(orm) if orm else None

    def buscar_por_curso(self, curso_id: str) -> Optional[Avaliacao]:
        orm = self._db.query(AvaliacaoORM).filter_by(curso_id=curso_id).first()
        return self._para_dominio(orm) if orm else None

    @staticmethod
    def _para_dominio(orm: AvaliacaoORM) -> Avaliacao:
        return Avaliacao(
            id=orm.id, curso_id=orm.curso_id, titulo=orm.titulo,
            nota_minima_aprovacao=orm.nota_minima_aprovacao,
            tentativas_maximas=orm.tentativas_maximas,
            questoes=[
                Questao(
                    id=q.id, enunciado=q.enunciado, tipo=TipoQuestao(q.tipo), peso=q.peso,
                    alternativas=[
                        Alternativa(id=a.id, texto=a.texto, correta=a.correta)
                        for a in q.alternativas
                    ],
                ) for q in orm.questoes
            ],
        )


class RepositorioDeTentativaSQLite(RepositorioDeTentativa):
    def __init__(self, db: Session):
        self._db = db

    def salvar(self, tentativa: Tentativa) -> Tentativa:
        orm = TentativaORM(
            id=tentativa.id, avaliacao_id=tentativa.avaliacao_id,
            estudante_id=tentativa.estudante_id, status=tentativa.status.value,
            nota=tentativa.nota,
            respostas=[
                RespostaQuestaoORM(
                    id=r.id, tentativa_id=tentativa.id,
                    questao_id=r.questao_id, alternativa_id=r.alternativa_id,
                ) for r in tentativa.respostas
            ],
        )
        self._db.merge(orm)
        self._db.commit()
        return tentativa

    def buscar_por_id(self, tentativa_id: str) -> Optional[Tentativa]:
        orm = self._db.query(TentativaORM).filter_by(id=tentativa_id).first()
        if not orm:
            return None
        return Tentativa(
            id=orm.id, avaliacao_id=orm.avaliacao_id,
            estudante_id=orm.estudante_id, status=StatusTentativa(orm.status), nota=orm.nota,
            respostas=[
                RespostaQuestao(id=r.id, questao_id=r.questao_id, alternativa_id=r.alternativa_id)
                for r in orm.respostas
            ],
        )

    def contar_tentativas(self, estudante_id: str, avaliacao_id: str) -> int:
        return self._db.query(TentativaORM).filter_by(
            estudante_id=estudante_id, avaliacao_id=avaliacao_id
        ).count()