from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from adapters.input.http.lab_exam_router import router as lab_exam_router
from adapters.input.http.nutrition_plan_router import router as nutrition_plan_router
from adapters.input.http.patient_router import router as patient_router
from config.database import create_tables
from config.settings import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Personalized AI-powered nutrition planning based on laboratory exam results.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patient_router, prefix="/api/v1")
app.include_router(lab_exam_router, prefix="/api/v1")
app.include_router(nutrition_plan_router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "version": settings.app_version}