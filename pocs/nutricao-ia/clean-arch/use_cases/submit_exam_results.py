import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from entities.exam import Exam, ExamMarker
from use_cases.ports.exam_repository_port import ExamRepositoryPort
from use_cases.ports.patient_repository_port import PatientRepositoryPort


@dataclass
class ExamMarkerInput:
    name: str
    value: float
    unit: str
    reference_min: float
    reference_max: float


@dataclass
class SubmitExamInput:
    patient_id: str
    exam_date: datetime
    lab_name: str
    markers: List[ExamMarkerInput] = field(default_factory=list)


@dataclass
class SubmitExamOutput:
    exam: Exam
    abnormal_count: int
    critical_count: int


class SubmitExamResults:
    def __init__(
        self,
        patient_repository: PatientRepositoryPort,
        exam_repository: ExamRepositoryPort,
    ) -> None:
        self._patient_repo = patient_repository
        self._exam_repo = exam_repository

    def execute(self, input_data: SubmitExamInput) -> SubmitExamOutput:
        if not self._patient_repo.find_by_id(input_data.patient_id):
            raise ValueError(f"Paciente {input_data.patient_id} não encontrado")

        markers = [
            ExamMarker(
                name=m.name,
                value=m.value,
                unit=m.unit,
                reference_min=m.reference_min,
                reference_max=m.reference_max,
            )
            for m in input_data.markers
        ]

        exam = Exam(
            id=str(uuid.uuid4()),
            patient_id=input_data.patient_id,
            exam_date=input_data.exam_date,
            lab_name=input_data.lab_name,
            markers=markers,
        )
        exam.validate()

        saved = self._exam_repo.save(exam)
        return SubmitExamOutput(
            exam=saved,
            abnormal_count=len(saved.abnormal_markers),
            critical_count=len(saved.critical_markers),
        )