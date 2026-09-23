from dataclasses import dataclass
from datetime import date
from enum import Enum


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


@dataclass
class Patient:
    id: str
    name: str
    birth_date: date
    gender: Gender
    weight_kg: float
    height_cm: float
    email: str

    @property
    def age(self) -> int:
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

    @property
    def bmi(self) -> float:
        return round(self.weight_kg / ((self.height_cm / 100) ** 2), 2)

    @property
    def bmi_classification(self) -> str:
        bmi = self.bmi
        if bmi < 18.5:
            return "Abaixo do peso"
        elif bmi < 25.0:
            return "Peso normal"
        elif bmi < 30.0:
            return "Sobrepeso"
        return "Obesidade"

    def validate(self) -> None:
        if not self.name.strip():
            raise ValueError("Nome do paciente não pode ser vazio")
        if self.weight_kg <= 0:
            raise ValueError("Peso deve ser positivo")
        if self.height_cm <= 0:
            raise ValueError("Altura deve ser positiva")
        if self.birth_date >= date.today():
            raise ValueError("Data de nascimento deve estar no passado")