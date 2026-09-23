from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from entities.certificate import Certificate


class CertificateRepository(ABC):

    @abstractmethod
    def save(self, certificate: Certificate) -> Certificate: ...

    @abstractmethod
    def find_by_id(self, certificate_id: UUID) -> Optional[Certificate]: ...

    @abstractmethod
    def find_by_hash(self, verification_hash: str) -> Optional[Certificate]: ...

    @abstractmethod
    def find_by_student_id(self, student_id: UUID) -> list[Certificate]: ...

    @abstractmethod
    def update(self, certificate: Certificate) -> Certificate: ...