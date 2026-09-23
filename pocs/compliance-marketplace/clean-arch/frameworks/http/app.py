from fastapi import FastAPI

from frameworks.config import settings
from frameworks.database.connection import create_tables
from frameworks.http.routes import (
    client_routes,
    freelancer_routes,
    project_routes,
    proposal_routes,
)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_title,
        version=settings.app_version,
        description=(
            "Marketplace connecting companies with freelancers "
            "specialized in regulatory compliance (LGPD, GDPR, SOX, PCI-DSS, etc.)"
        ),
    )

    create_tables()

    app.include_router(freelancer_routes.router)
    app.include_router(client_routes.router)
    app.include_router(project_routes.router)
    app.include_router(proposal_routes.router)

    @app.get("/health", tags=["Health"])
    def health_check() -> dict:
        return {"status": "healthy", "version": settings.app_version}

    return app