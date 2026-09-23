from fastapi import FastAPI

from frameworks.db.database import create_tables
from frameworks.http.routers import (
    certificate_router,
    course_router,
    issuer_router,
    student_router,
)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Plataforma de Certificação Digital de Cursos Livres",
        description=(
            "Emissão e verificação pública de certificados digitais para cursos livres. "
            "Verificação disponível sem autenticação em GET /certificates/verify/{hash}."
        ),
        version="1.0.0",
    )

    create_tables()

    app.include_router(issuer_router.router)
    app.include_router(course_router.router)
    app.include_router(student_router.router)
    app.include_router(certificate_router.router)

    return app