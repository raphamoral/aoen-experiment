from abc import ABC, abstractmethod
from typing import List, Optional

from entities.exam import Exam


class ExamRepositoryPort(ABC):

    @abstractmethod
    def save(self, exam: Exam) -> Exam: ...

    @abstractmethod
    def find_by_id(self, exam_id: str) -> Optional[Exam]: ...

    @abstractmethod
    def find_by_patient_id(self, patient_id: str) -> List[Exam]: ...

    @abstractmethod
    def find_latest_by_patient_id(self, patient_id: str) -> Optional[Exam]: ...