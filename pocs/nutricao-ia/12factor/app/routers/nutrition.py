"""Endpoints de recomendações nutricionais com IA."""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.schemas import NutritionRecommendationOut
from app.services.nutrition_service import generate_recommendation, get_recommendation_by_exam
from app.dependencies import get_current_user

router = APIRouter()


@router.post("/analyze/{exam_id}", response_model=NutritionRecommendationOut, status_code=status.HTTP_201_CREATED)
async def analyze_exam(
    exam_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Envia exame para análise pela IA e retorna recomendações nutricionais.
    Idempotente via cache Redis — re-chamadas retornam resultado existente.
    """
    try:
        return await generate_recommendation(db, current_user, exam_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/exam/{exam_id}", response_model=NutritionRecommendationOut)
async def get_recommendation(
    exam_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rec = await get_recommendation_by_exam(db, current_user.id, exam_id)
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhuma recomendação encontrada para este exame")
    return rec