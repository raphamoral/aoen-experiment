from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.router import api_router
from src.config import get_settings
from src.infrastructure.database import init_db


def create_app() -> FastAPI:
    """
    Factory de aplicação — decisão reversível: permite múltiplas instâncias
    (testes, ambientes diferentes) sem estado global.
    """
    settings = get_settings()

    app = FastAPI(
        title="Compliance Freelancer Marketplace",
        description="Marketplace de freelancers especializados em compliance regulatório",
        version="0.1.0",
        docs_url="/docs" if settings.debug else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api/v1")

    @app.on_event("startup")
    async def on_startup():
        await init_db()

    return app