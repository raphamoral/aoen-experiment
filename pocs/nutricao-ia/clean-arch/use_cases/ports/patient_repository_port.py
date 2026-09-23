from abc import ABC, abstractmethod
from typing import List, Optional

from entities.patient import Patient


class PatientRepositoryPort(ABC):

    @abstractmethod
    def save(self, patient: Patient) -> Patient: ...

    @abstractmethod
    def find_by_id(self, patient_id: str) -> Optional[Patient]: ...

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[Patient]: ...

    @abstractmethod
    def find_all(self) -> List[Patient]: ...

    @abstractmethod
    def delete(self, patient_id: str) -> None: ...