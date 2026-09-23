from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from database import engine, Base
from routers import patients, exams, nutrition

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("NutriAI initialized — tabelas prontas")
    yield
    await engine.dispose()


settings = get_settings()

app = FastAPI(
    title="NutriAI",
    description="Planos nutricionais personalizados baseados em análise de biomarcadores com IA",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def inject_tenant(request: Request, call_next):
    # FASE 3 — CONFIG-DRIVEN: tenant identificado via header, sem alterar rotas
    request.state.tenant_id = request.headers.get("X-Tenant-ID", "default")
    return await call_next(request)


app.include_router(patients.router, prefix="/api/v1/patients", tags=["Pacientes"])
app.include_router(exams.router, prefix="/api/v1/exams", tags=["Exames"])
app.include_router(nutrition.router, prefix="/api/v1/nutrition", tags=["Nutrição"])


@app.get("/health", tags=["Sistema"])
async def health():
    return {"status": "healthy", "service": "NutriAI", "version": "1.0.0"}