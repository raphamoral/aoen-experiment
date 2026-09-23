import logging
import sys

from fastapi import FastAPI

from app.config import settings
from app.database import engine, Base
from app.routers import auth, freelancers, health, projects

# 12-factor XI: Logs — tratar como stream de eventos para stdout
logging.basicConfig(
    stream=sys.stdout,
    level=settings.LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        # Docs apenas em dev — paridade dev/prod controlada por env var
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    @app.on_event("startup")
    async def startup() -> None:
        # 12-factor IX: Descartabilidade — startup rápido
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @app.on_event("shutdown")
    async def shutdown() -> None:
        # Graceful shutdown — liberar recursos de backing services
        await engine.dispose()

    app.include_router(health.router, tags=["health"])
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(freelancers.router, prefix="/api/v1/freelancers", tags=["freelancers"])
    app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])

    return app