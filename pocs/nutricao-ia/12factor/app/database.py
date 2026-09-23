"""
Factor IV: Backing services — banco de dados tratado como recurso anexado.
Conexão via DATABASE_URL; troca de provider não exige mudança de código.
"""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import settings


engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # detecta conexões mortas sem estado local
    echo=settings.APP_DEBUG,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """Dependency injection — sessão por request, sem estado entre requests."""
    async with AsyncSessionLocal() as session:
        yield session