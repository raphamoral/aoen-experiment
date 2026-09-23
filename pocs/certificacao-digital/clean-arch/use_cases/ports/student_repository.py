from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from entities.student import Student


class StudentRepository(ABC):

    @abstractmethod
    def save(self, student: Student) -> Student: ...

    @abstractmethod
    def find_by_id(self, student_id: UUID) -> Optional[Student]: ...

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[Student]: ...