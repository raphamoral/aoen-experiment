from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from adapters.output.persistence.models import LabExamModel
from domain.entities.lab_exam import ExamResult, LabExam
from ports.output.lab_exam_repository_port import LabExamRepositoryPort


class SQLAlchemyLabExamRepository(LabExamRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _result_to_dict(self, result: ExamResult) -> dict:
        return {
            "exam_type": result.exam_type,
            "value": result.value,
            "unit": result.unit,
            "reference_min": result.reference_min,
            "reference_max": result.reference_max,
        }

    def _dict_to_result(self, data: dict) -> ExamResult:
        return ExamResult(
            exam_type=data["exam_type"],
            value=data["value"],
            unit=data["unit"],
            reference_min=data.get("reference_min"),
            reference_max=data.get("reference_max"),
        )

    def _to_domain(self, model: LabExamModel) -> LabExam:
        return LabExam(
            id=model.id,
            patient_id=model.patient_id,
            exam_date=model.exam_date,
            results=[self._dict_to_result(r) for r in model.results],
            created_at=model.created_at,
        )

    def _to_model(self, exam: LabExam) -> LabExamModel:
        return LabExamModel(
            id=exam.id,
            patient_id=exam.patient_id,
            exam_date=exam.exam_date,
            results=[self._result_to_dict(r) for r in exam.results],
            created_at=exam.created_at,
        )

    async def save(self, exam: LabExam) -> LabExam:
        model = self._to_model(exam)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def find_by_id(self, exam_id: UUID) -> LabExam | None:
        result = await self._session.execute(
            select(LabExamModel).where(LabExamModel.id == exam_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def find_by_patient_id(self, patient_id: UUID) -> list[LabExam]:
        result = await self._session.execute(
            select(LabExamModel).where(LabExamModel.patient_id == patient_id)
        )
        return [self._to_domain(m) for m in result.scalars().all()]