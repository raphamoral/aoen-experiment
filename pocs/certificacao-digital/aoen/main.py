"""
AOEN — Plataforma de Certificação Digital de Cursos Livres

Ponto de entrada da aplicação FastAPI.
Responsabilidades deste arquivo: montar routers, configurar middlewares, inicializar DB.
Zero lógica de negócio aqui.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from database import create_tables
from routers import certificates, courses, tenants, verification

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria tabelas no startup (substitua por Alembic em produção)
    create_tables()
    yield


app = FastAPI(
    title="CertChain — Certificação Digital de Cursos Livres",
    description=(
        "Plataforma multi-tenant para emissão e verificação pública de certificados "
        "digitais com assinatura Ed25519. Construída segundo o framework AOEN."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# MULTI-INTERFACE: rota de verificação pública sem prefixo de versão
app.include_router(verification.router)

# API v1 — routers de gerenciamento
for router in (tenants.router, courses.router, certificates.router):
    app.include_router(router, prefix=settings.api_v1_prefix)