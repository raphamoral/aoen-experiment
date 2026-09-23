"""
Factor VI: Processos stateless — nenhum estado local, tudo em backing services.
Factor VII: Port binding — a aplicação é self-contained e exporta serviço via porta.
"""
import structlog
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.routers import exams, nutrition, users
from app.logging_config import configure_logging

configure_logging()
log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Factor IX: Disposability — startup rápido, shutdown gracioso."""
    log.info("startup", env=settings.APP_ENV, version="1.0.0")
    yield
    log.info("shutdown")
    await engine.dispose()


app = FastAPI(
    title="NutriAI — Nutrição Personalizada com IA",
    description="Recomendações nutricionais baseadas em exames laboratoriais via IA.",
    version="1.0.0",
    docs_url="/docs" if settings.APP_ENV != "production" else None,
    redoc_url="/redoc" if settings.APP_ENV != "production" else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(exams.router, prefix="/api/v1/exams", tags=["exams"])
app.include_router(nutrition.router, prefix="/api/v1/nutrition", tags=["nutrition"])


@app.get("/healthz")
async def healthcheck():
    """Liveness probe para orquestradores (Kubernetes, Heroku, etc.)."""
    return {"status": "ok", "env": settings.APP_ENV}