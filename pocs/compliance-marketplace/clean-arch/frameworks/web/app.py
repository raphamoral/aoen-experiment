from contextlib import asynccontextmanager
from fastapi import FastAPI

from frameworks.database.session import create_tables
from frameworks.web.routes import (
    freelancer_routes,
    client_routes,
    project_routes,
    proposal_routes,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Compliance Freelancer Marketplace",
        description=(
            "Marketplace connecting companies that need regulatory compliance expertise "
            "with specialized freelancers (LGPD, GDPR, SOX, BACEN, CVM, ISO 27001 and more)."
        ),
        version="1.0.0",
        lifespan=lifespan,
    )

    app.include_router(freelancer_routes.router)
    app.include_router(client_routes.router)
    app.include_router(project_routes.router)
    app.include_router(proposal_routes.router)

    return app