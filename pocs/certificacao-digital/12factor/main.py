import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine
from app.routers.certificates import router as certificates_router
from app.routers.verification import router as verification_router

settings = get_settings()

# Factor XI: logs como fluxo de eventos — somente stdout, sem arquivos
logging.basicConfig(
    stream=sys.stdout,
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Factor IX: descartabilidade — inicialização rápida
    logger.info("startup env=%s app=%s", settings.environment, settings.app_name)
    Base.metadata.create_all(bind=engine)
    yield
    logger.info("shutdown app=%s", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    description="Plataforma de certificação digital de cursos livres com verificação pública",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url=None,
)

# Factor III: origens CORS configuradas via variável de ambiente
origins = [o.strip() for o in settings.allowed_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(certificates_router)
app.include_router(verification_router)


@app.get("/health", tags=["ops"])
def health():
    # Factor IX: endpoint leve para orquestradores verificarem liveness
    return {"status": "ok", "environment": settings.environment}