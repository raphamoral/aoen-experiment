import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.infra.database import create_tables
from contexts.laboratory.api.router import router as lab_router
from contexts.nutrition.api.router import router as nutrition_router
from contexts.ai_analysis.api.router import router as analysis_router
from contexts.user_profile.api.router import router as user_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NutriAI — Nutrição Personalizada por Exames Laboratoriais",
    description="""
## Architecture for Flow (DDD + Wardley Mapping + Team Topologies)

### Bounded Contexts

| Contexto | Wardley | Team Topology | Responsabilidade |
|---|---|---|---|
| `ai_analysis` | **Genesis** | Complicated Subsystem | Insights clínicos via IA |
| `laboratory` | **Custom** | Stream-aligned | Ingestão de biomarcadores |
| `nutrition` | **Custom** | Stream-aligned | Planos nutricionais terapêuticos |
| `user_profile` | **Product** | Platform | Contexto clínico compartilhado |

### Fluxo de Valor Principal

```
Perfil → Exame Laboratorial → Análise IA → Plano Nutricional
```

Contexts se comunicam exclusivamente via **Eventos de Domínio**,
garantindo acoplamento fraco e evolução independente.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    create_tables()
    _register_cross_context_handlers()
    logger.info("NutriAI iniciado. Bounded contexts carregados.")


def _register_cross_context_handlers() -> None:
    """Registra handlers de eventos entre bounded contexts.

    Esta função materializa as dependências entre contexts via eventos,
    mantendo acoplamento fraco (eventual consistency).

    Em produção: substitua por consumers Kafka/SQS separados por context,
    permitindo deploy independente de cada bounded context.
    """
    from shared.events.event_bus import event_bus
    from contexts.laboratory.domain.events import LabResultReceived, BiomarkerOutOfRange
    from contexts.ai_analysis.domain.events import AnalysisGenerated, CriticalInsightFound

    async def on_lab_result_received(event: LabResultReceived) -> None:
        logger.info(
            "[laboratory → ai_analysis] LabResultReceived: usuário=%s, exame=%s",
            event.user_id,
            event.lab_result_id,
        )

    async def on_biomarker_out_of_range(event: BiomarkerOutOfRange) -> None:
        logger.info(
            "[laboratory → nutrition] BiomarkerOutOfRange: %s=%s (%s)",
            event.biomarker_name,
            event.value,
            event.status,
        )

    async def on_analysis_generated(event: AnalysisGenerated) -> None:
        logger.info(
            "[ai_analysis → *] AnalysisGenerated: %d insights, crítico=%s",
            event.insight_count,
            event.has_critical,
        )

    async def on_critical_insight_found(event: CriticalInsightFound) -> None:
        logger.warning(
            "[ai_analysis → notificação] CRÍTICO: %s — usuário=%s",
            event.insight_title,
            event.user_id,
        )

    event_bus.subscribe(LabResultReceived, on_lab_result_received)
    event_bus.subscribe(BiomarkerOutOfRange, on_biomarker_out_of_range)
    event_bus.subscribe(AnalysisGenerated, on_analysis_generated)
    event_bus.subscribe(CriticalInsightFound, on_critical_insight_found)


app.include_router(user_router)
app.include_router(lab_router)
app.include_router(nutrition_router)
app.include_router(analysis_router)


@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "NutriAI",
        "architecture": "Architecture for Flow",
        "principles": ["DDD", "Wardley Mapping", "Team Topologies"],
        "bounded_contexts": ["user_profile", "laboratory", "nutrition", "ai_analysis"],
        "docs": "/docs",
    }