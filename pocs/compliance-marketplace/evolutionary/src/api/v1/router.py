from fastapi import APIRouter

from src.api.v1 import freelancers, projects, proposals, health

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(freelancers.router, prefix="/freelancers", tags=["freelancers"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(proposals.router, prefix="/proposals", tags=["proposals"])