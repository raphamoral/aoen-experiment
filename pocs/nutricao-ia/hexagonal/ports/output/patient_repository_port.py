from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.patient import Patient


class PatientRepositoryPort(ABC):
    @abstractmethod
    async def save(self, patient: Patient) -> Patient:
        ...

    @abstractmethod
    async def find_by_id(self, patient_id: UUID) -> Patient | None:
        ...

    @abstractmethod
    async def find_by_email(self, email: str) -> Patient | None:
        ...