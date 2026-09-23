from abc import ABC, abstractmethod
from dataclasses import dataclass

from domain.entities.patient import Patient


@dataclass
class RegisterPatientCommand:
    name: str
    email: str
    age: int
    gender: str
    health_goals: list[str]


class RegisterPatientUseCasePort(ABC):
    @abstractmethod
    async def execute(self, command: RegisterPatientCommand) -> Patient:
        ...