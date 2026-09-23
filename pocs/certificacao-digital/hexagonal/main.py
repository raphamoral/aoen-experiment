import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI

from adapters.inbound.http.router import router
from adapters.outbound.persistence.database import create_tables

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting up — creating database tables if needed.")
    create_tables()
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="Plataforma de Certificação Digital de Cursos Livres",
    description=(
        "Emissão e verificação pública de certificados digitais com hash "
        "SHA-256 à prova de adulteração."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router, prefix="/api/v1")


@app.get("/health", tags=["Meta"])
def health() -> dict:
    return {"status": "healthy"}