from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.kernel.infrastructure.database import create_tables
from contexts.course_catalog.api.router import router as course_catalog_router
from contexts.enrollment.api.router import router as enrollment_router
from contexts.assessment.api.router import router as assessment_router
from contexts.certification.api.router import router as certification_router
from contexts.verification.api.router import router as verification_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    from contexts.certification.application.event_handlers import configurar_handlers
    configurar_handlers()
    yield


app = FastAPI(
    title="Plataforma de Certificação Digital",
    description="Certificação digital de cursos livres com verificação pública",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fluxo de valor: Catálogo → Matrícula → Avaliação → Certificação → Verificação
app.include_router(course_catalog_router, prefix="/api/v1/catalogo", tags=["Catálogo de Cursos"])
app.include_router(enrollment_router, prefix="/api/v1/matriculas", tags=["Matrículas"])
app.include_router(assessment_router, prefix="/api/v1/avaliacoes", tags=["Avaliações"])
app.include_router(certification_router, prefix="/api/v1/certificados", tags=["Certificados"])
app.include_router(verification_router, prefix="/api/v1/verificacao", tags=["Verificação Pública"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "plataforma-certificacao-digital"}