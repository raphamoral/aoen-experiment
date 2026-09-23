from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.routes import certificates, courses, verification
from src.infrastructure.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="CertChain — Plataforma de Certificação Digital",
    description=(
        "Emissão e verificação pública de certificados digitais para cursos livres. "
        "Cada certificado possui hash HMAC-SHA256 único verificável sem autenticação."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(courses.router, prefix="/courses", tags=["courses"])
app.include_router(certificates.router, prefix="/certificates", tags=["certificates"])
app.include_router(verification.router, prefix="/verify", tags=["verification"])


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}