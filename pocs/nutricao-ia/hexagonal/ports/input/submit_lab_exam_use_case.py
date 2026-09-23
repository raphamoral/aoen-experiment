from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from uuid import UUID

from domain.entities.lab_exam import LabExam


@dataclass
class ExamResultInput:
    exam_type: str
    value: float
    unit: str
    reference_min: float | None = None
    reference_max: float | None = None


@dataclass
class SubmitLabExamCommand:
    patient_id: UUID
    exam_date: date
    results: list[ExamResultInput]


class SubmitLabExamUseCasePort(ABC):
    @abstractmethod
    async def execute(self, command: SubmitLabExamCommand) -> LabExam:
        ...