from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

from frameworks.api.routes import exam_routes, nutrition_routes, patient_routes
from frameworks.db.connection import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="Nutrition AI API",
    description="Plano nutricional personalizado com IA baseado em exames laboratoriais",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(patient_routes.router)
app.include_router(exam_routes.router)
app.include_router(nutrition_routes.router)


@app.get("/health", tags=["infra"])
def health_check():
    return {"status": "healthy"}