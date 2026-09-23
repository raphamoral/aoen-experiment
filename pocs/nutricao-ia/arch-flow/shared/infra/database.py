from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:///./nutri_ai.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    from contexts.laboratory.infrastructure.repository import LabResultModel
    from contexts.nutrition.infrastructure.repository import NutritionalPlanModel
    from contexts.ai_analysis.infrastructure.repository import AnalysisModel
    from contexts.user_profile.infrastructure.repository import UserProfileModel

    Base.metadata.create_all(bind=engine)