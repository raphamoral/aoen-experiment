from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.middleware import ResponseTimeMiddleware
from src.api.routes import exams, nutrition, users
from src.config import settings
from src.infrastructure.database import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Nutrição personalizada baseada em exames laboratoriais e IA",
    version=settings.VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Decisão reversível: restringir em produção via ALLOWED_ORIGINS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(ResponseTimeMiddleware)

app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(exams.router, prefix="/api/v1/exams", tags=["exams"])
app.include_router(nutrition.router, prefix="/api/v1/nutrition", tags=["nutrition"])


@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "ai_provider": settings.AI_PROVIDER,
    }