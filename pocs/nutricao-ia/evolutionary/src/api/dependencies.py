"""
Wiring layer — único arquivo com alto acoplamento intencional.
Responsabilidade: montar o grafo de dependências via FastAPI DI.
Fitness function de acoplamento exclui este arquivo explicitamente.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database import get_db
from src.repositories.exam_repository import ExamRepository
from src.repositories.nutrition_repository import NutritionPlanRepository
from src.repositories.user_repository import UserRepository
from src.services.exam_service import ExamService
from src.services.nutrition_service import NutritionService


def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_exam_repo(db: AsyncSession = Depends(get_db)) -> ExamRepository:
    return ExamRepository(db)


def get_plan_repo(db: AsyncSession = Depends(get_db)) -> NutritionPlanRepository:
    return NutritionPlanRepository(db)


def get_exam_service(repo: ExamRepository = Depends(get_exam_repo)) -> ExamService:
    return ExamService(repo)


def get_nutrition_service(
    user_repo: UserRepository = Depends(get_user_repo),
    exam_repo: ExamRepository = Depends(get_exam_repo),
    plan_repo: NutritionPlanRepository = Depends(get_plan_repo),
) -> NutritionService:
    return NutritionService(user_repo, exam_repo, plan_repo)