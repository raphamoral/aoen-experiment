"""Serviço de exames — lógica de negócio isolada da camada HTTP."""
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import LabExam
from app.schemas import LabExamCreate


async def create_exam(db: AsyncSession, user_id: uuid.UUID, data: LabExamCreate) -> LabExam:
    exam = LabExam(
        user_id=user_id,
        exam_date=data.exam_date,
        lab_name=data.lab_name,
        markers={k: v.model_dump() for k, v in data.markers.items()},
    )
    db.add(exam)
    await db.commit()
    await db.refresh(exam)
    return exam


async def get_exam(db: AsyncSession, exam_id: uuid.UUID, user_id: uuid.UUID) -> LabExam | None:
    result = await db.execute(
        select(LabExam).where(LabExam.id == exam_id, LabExam.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def list_exams(db: AsyncSession, user_id: uuid.UUID) -> list[LabExam]:
    result = await db.execute(
        select(LabExam).where(LabExam.user_id == user_id).order_by(LabExam.exam_date.desc())
    )
    return list(result.scalars().all())