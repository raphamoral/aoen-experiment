import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from frameworks.db.models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./certifica.db")

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)