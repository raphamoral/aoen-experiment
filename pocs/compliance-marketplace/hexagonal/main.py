import logging

from fastapi import FastAPI

from adapters.inbound.http.freelancer_router import router as freelancer_router
from adapters.inbound.http.project_router import router as project_router
from adapters.inbound.http.proposal_router import router as proposal_router
from container import wire_dependencies

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(
    title="Marketplace de Freelancers em Compliance Regulatório",
    description=(
        "Plataforma que conecta empresas a especialistas independentes em "
        "LGPD, GDPR, SOX, Basel III, AML/KYC e outras regulações. "
        "Arquitetura Hexagonal (Ports & Adapters) de Alistair Cockburn."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Conecta adaptadores concretos às portas abstratas
wire_dependencies(app)

# Registra os adaptadores de entrada HTTP
app.include_router(freelancer_router)
app.include_router(project_router)
app.include_router(proposal_router)


@app.get("/health", tags=["Infra"])
def health_check():
    return {"status": "ok"}