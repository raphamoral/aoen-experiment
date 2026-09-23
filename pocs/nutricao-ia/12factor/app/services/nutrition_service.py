"""
Serviço de recomendações nutricionais.
Factor VI: Stateless — lê do banco, chama IA, persiste resultado. Sem estado em memória.
"""
import uuid
import json
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import LabExam, NutritionRecommendation, User
from app.services.ai_service import analyze_exam_with_ai
from app.cache import cache_get, cache_set
from app.config import settings

log = structlog.get_logger()


def _cache_key(exam_id: uuid.UUID) -> str:
    return f"nutrition:recommendation:{exam_id}"


async def generate_recommendation(
    db: AsyncSession,
    user: User,
    exam_id: uuid.UUID,
) -> NutritionRecommendation:
    # Verifica cache (backing service Redis — Factor IV)
    cached = await cache_get(_cache_key(exam_id))
    if cached:
        log.info("cache_hit", exam_id=str(exam_id))
        rec_id = uuid.UUID(json.loads(cached)["id"])
        result = await db.execute(
            select(NutritionRecommendation).where(NutritionRecommendation.id == rec_id)
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing

    exam = await db.get(LabExam, exam_id)
    if not exam or exam.user_id != user.id:
        raise ValueError("Exame não encontrado ou sem permissão")

    user_profile = {
        "full_name": user.full_name,
        "age": user.age,
        "weight_kg": user.weight_kg,
        "height_cm": user.height_cm,
    }

    ai_result = await analyze_exam_with_ai(user_profile, exam.markers)

    recommendation = NutritionRecommendation(
        user_id=user.id,
        exam_id=exam_id,
        ai_model=settings.ANTHROPIC_MODEL,
        summary=ai_result.get("summary", ""),
        recommendations=ai_result,
    )
    db.add(recommendation)
    await db.commit()
    await db.refresh(recommendation)

    # Persiste no cache (TTL 1h — Factor VI: sem estado local)
    await cache_set(_cache_key(exam_id), json.dumps({"id": str(recommendation.id)}), ttl_seconds=3600)

    log.info("recommendation_created", recommendation_id=str(recommendation.id), exam_id=str(exam_id))
    return recommendation


async def get_recommendation_by_exam(
    db: AsyncSession,
    user_id: uuid.UUID,
    exam_id: uuid.UUID,
) -> NutritionRecommendation | None:
    result = await db.execute(
        select(NutritionRecommendation).where(
            NutritionRecommendation.exam_id == exam_id,
            NutritionRecommendation.user_id == user_id,
        ).order_by(NutritionRecommendation.created_at.desc())
    )
    return result.scalars().first()