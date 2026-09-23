from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from database import engine, Base
from routers import freelancers, projects, matches, tenants


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="ComplianceMatch",
        description="Marketplace de freelancers especializados em compliance regulatório",
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

    app.include_router(tenants.router, prefix="/api/v1/tenants", tags=["tenants"])
    app.include_router(freelancers.router, prefix="/api/v1/freelancers", tags=["freelancers"])
    app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
    app.include_router(matches.router, prefix="/api/v1/matches", tags=["matches"])

    return app


app = create_app()