from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.nutrition import NutritionPlan
from src.repositories.base import BaseRepository


class NutritionPlanRepository(BaseRepository[NutritionPlan]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(NutritionPlan, session)

    async def list_by_user(self, user_id: int) -> list[NutritionPlan]:
        result = await self.session.execute(
            select(NutritionPlan)
            .where(NutritionPlan.user_id == user_id)
            .order_by(NutritionPlan.created_at.desc())
        )
        return list(result.scalars().all())

    async def list(self, limit: int = 100, offset: int = 0) -> list[NutritionPlan]:
        result = await self.session.execute(
            select(NutritionPlan).limit(limit).offset(offset)
        )
        return list(result.scalars().all())