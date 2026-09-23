import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Decisão: SQLite por padrão (Last Responsible Moment).
# Migrar para PostgreSQL requer apenas alterar DATABASE_URL — nenhum outro módulo muda.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./certifications.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from src.domain import models  # noqa: F401 — necessário para registrar os modelos no Base
    Base.metadata.create_all(bind=engine)