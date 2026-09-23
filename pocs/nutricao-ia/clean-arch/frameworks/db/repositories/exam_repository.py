from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from entities.exam import Exam, ExamMarker
from frameworks.db.models import ExamModel
from use_cases.ports.exam_repository_port import ExamRepositoryPort


class SqlAlchemyExamRepository(ExamRepositoryPort):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, exam: Exam) -> Exam:
        self._session.add(
            ExamModel(
                id=exam.id,
                patient_id=exam.patient_id,
                exam_date=exam.exam_date,
                lab_name=exam.lab_name,
                markers=[
                    {
                        "name": m.name,
                        "value": m.value,
                        "unit": m.unit,
                        "reference_min": m.reference_min,
                        "reference_max": m.reference_max,
                    }
                    for m in exam.markers
                ],
            )
        )
        self._session.commit()
        return exam

    def find_by_id(self, exam_id: str) -> Optional[Exam]:
        model = self._session.query(ExamModel).filter_by(id=exam_id).first()
        return self._to_entity(model) if model else None

    def find_by_patient_id(self, patient_id: str) -> List[Exam]:
        models = (
            self._session.query(ExamModel)
            .filter_by(patient_id=patient_id)
            .order_by(ExamModel.exam_date.desc())
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_latest_by_patient_id(self, patient_id: str) -> Optional[Exam]:
        model = (
            self._session.query(ExamModel)
            .filter_by(patient_id=patient_id)
            .order_by(ExamModel.exam_date.desc())
            .first()
        )
        return self._to_entity(model) if model else None

    def _to_entity(self, model: ExamModel) -> Exam:
        return Exam(
            id=model.id,
            patient_id=model.patient_id,
            exam_date=model.exam_date
            if isinstance(model.exam_date, datetime)
            else datetime.fromisoformat(str(model.exam_date)),
            lab_name=model.lab_name,
            markers=[
                ExamMarker(
                    name=m["name"],
                    value=m["value"],
                    unit=m["unit"],
                    reference_min=m["reference_min"],
                    reference_max=m["reference_max"],
                )
                for m in model.markers
            ],
        )