from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.lab_exam import LabExam


class LabExamRepositoryPort(ABC):
    @abstractmethod
    async def save(self, exam: LabExam) -> LabExam:
        ...

    @abstractmethod
    async def find_by_id(self, exam_id: UUID) -> LabExam | None:
        ...

    @abstractmethod
    async def find_by_patient_id(self, patient_id: UUID) -> list[LabExam]:
        ...