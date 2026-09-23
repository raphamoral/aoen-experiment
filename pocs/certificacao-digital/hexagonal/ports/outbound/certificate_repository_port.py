from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.certificate import Certificate


class CertificateRepositoryPort(ABC):
    @abstractmethod
    def save(self, certificate: Certificate) -> None:
        ...

    @abstractmethod
    def update(self, certificate: Certificate) -> None:
        ...

    @abstractmethod
    def find_by_id(self, certificate_id: str) -> Optional[Certificate]:
        ...

    @abstractmethod
    def find_by_hash(self, certificate_hash: str) -> Optional[Certificate]:
        ...

    @abstractmethod
    def find_by_student_id(self, student_id: str) -> List[Certificate]:
        ...

    @abstractmethod
    def find_active_by_student_and_course(
        self, student_id: str, course_id: str
    ) -> Optional[Certificate]:
        ...