from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.infrastructure.config import settings
from shared.infrastructure.database import init_db

from contexts.identity.api.router import router as identity_router
from contexts.freelancer.api.router import router as freelancer_router
from contexts.compliance_catalog.api.router import router as catalog_router
from contexts.compliance_catalog.application.services import ComplianceCatalogService
from contexts.compliance_catalog.infrastructure.repository import RegulatoryFrameworkRepository
from contexts.matching.api.router import router as matching_router
from contexts.contracting.api.router import router as contracting_router
from contexts.payment.api.router import router as payment_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    # Seed do catálogo regulatório brasileiro na inicialização
    repo = RegulatoryFrameworkRepository()
    catalog_service = ComplianceCatalogService(repo)
    await catalog_service.seed_brazilian_frameworks()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
## ComplianceHub — Marketplace de Freelancers em Compliance Regulatório

Arquitetura baseada em **Architecture for Flow** (Susanne Kaiser):
**DDD + Wardley Mapping + Team Topologies**

---

### Bounded Contexts por Maturidade Wardley

| Contexto              | Maturidade | Time Topologies     |
|-----------------------|------------|---------------------|
| Matching              | Genesis    | Complicated Subsystem |
| Freelancer Profile    | Custom     | Stream-aligned      |
| Compliance Catalog    | Custom     | Stream-aligned      |
| Contracting           | Product    | Stream-aligned      |
| Identity              | Commodity  | Platform            |
| Payment               | Commodity  | Platform            |

### Fluxo de Valor Principal

```
Cliente define requisito regulatório
    → Matching ranqueia freelancers (Genesis: algoritmo proprietário)
    → Cliente aceita match
    → Contrato criado e assinado digitalmente (Product: ClickSign)
    → Freelancer entrega projeto de compliance
    → Pagamento liberado automaticamente (Commodity: Pagar.me)
```
    """,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(identity_router)
app.include_router(freelancer_router)
app.include_router(catalog_router)
app.include_router(matching_router)
app.include_router(contracting_router)
app.include_router(payment_router)


@app.get("/", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "architecture": "Architecture for Flow — DDD + Wardley Mapping + Team Topologies",
        "bounded_contexts": {
            "genesis": ["matching"],
            "custom": ["freelancer", "compliance_catalog"],
            "product": ["contracting"],
            "commodity": ["identity", "payment"],
        },
    }