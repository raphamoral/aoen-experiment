from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from entities.course import Course


class CourseRepository(ABC):

    @abstractmethod
    def save(self, course: Course) -> Course: ...

    @abstractmethod
    def find_by_id(self, course_id: UUID) -> Optional[Course]: ...

    @abstractmethod
    def find_by_issuer_id(self, issuer_id: UUID) -> list[Course]: ...