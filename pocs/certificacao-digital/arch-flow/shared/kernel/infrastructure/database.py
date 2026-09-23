from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_URL = "sqlite:///./certificacao_digital.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def create_tables() -> None:
    # Importações necessárias para que o SQLAlchemy registre os modelos ORM antes do create_all.
    # Em arquitetura distribuída: cada contexto gerencia sua própria migração (Alembic por contexto).
    from contexts.course_catalog.infrastructure.persistence import CursoORM, InstrutorORM  # noqa: F401
    from contexts.enrollment.infrastructure.persistence import MatriculaORM, RegistroDeProgressoORM  # noqa: F401
    from contexts.assessment.infrastructure.persistence import (  # noqa: F401
        AvaliacaoORM, QuestaoORM, AlternativaORM, TentativaORM, RespostaQuestaoORM,
    )
    from contexts.certification.infrastructure.persistence import CertificadoORM  # noqa: F401
    from contexts.verification.infrastructure.persistence import RegistroVerificacaoORM  # noqa: F401
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()