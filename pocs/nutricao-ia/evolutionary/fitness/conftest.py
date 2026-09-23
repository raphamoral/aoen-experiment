import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import src.models  # noqa: F401 — registra modelos antes de create_all
from main import app
from src.infrastructure.database import get_db
from src.models.base import Base


@pytest_asyncio.fixture
async def test_db():
    """Banco de dados SQLite in-memory isolado por teste. Descartado ao final."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()

    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_db: AsyncSession):
    """
    HTTP client com banco isolado em memória.
    Override do get_db garante que requisições usem a sessão de teste.
    """

    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()