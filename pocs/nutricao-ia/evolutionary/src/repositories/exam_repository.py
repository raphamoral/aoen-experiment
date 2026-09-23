from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.exam import ExamPanel, ExamResult
from src.repositories.base import BaseRepository


class ExamRepository(BaseRepository[ExamPanel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(ExamPanel, session)

    async def get_by_id(self, record_id: int) -> ExamPanel | None:
        result = await self.session.execute(
            select(ExamPanel)
            .where(ExamPanel.id == record_id)
            .options(selectinload(ExamPanel.results))
        )
        return result.scalar_one_or_none()

    async def list(self, limit: int = 100, offset: int = 0) -> list[ExamPanel]:
        result = await self.session.execute(
            select(ExamPanel).options(selectinload(ExamPanel.results)).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def list_by_user(self, user_id: int) -> list[ExamPanel]:
        result = await self.session.execute(
            select(ExamPanel)
            .where(ExamPanel.user_id == user_id)
            .options(selectinload(ExamPanel.results))
            .order_by(ExamPanel.exam_date.desc())
        )
        return list(result.scalars().all())

    async def create_with_results(
        self,
        user_id: int,
        exam_date,
        lab_name: str,
        notes: str,
        results: list[dict],
    ) -> ExamPanel:
        panel = ExamPanel(user_id=user_id, exam_date=exam_date, lab_name=lab_name, notes=notes)
        self.session.add(panel)
        await self.session.flush()

        for r in results:
            self.session.add(ExamResult(panel_id=panel.id, **r))

        await self.session.flush()
        await self.session.refresh(panel)
        return panel