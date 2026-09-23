import uuid
from dataclasses import dataclass
from datetime import date

from entities.patient import Gender, Patient
from use_cases.ports.patient_repository_port import PatientRepositoryPort


@dataclass
class RegisterPatientInput:
    name: str
    birth_date: date
    gender: str
    weight_kg: float
    height_cm: float
    email: str


@dataclass
class RegisterPatientOutput:
    patient: Patient


class RegisterPatient:
    def __init__(self, patient_repository: PatientRepositoryPort) -> None:
        self._repository = patient_repository

    def execute(self, input_data: RegisterPatientInput) -> RegisterPatientOutput:
        if self._repository.find_by_email(input_data.email):
            raise ValueError(f"Paciente com email {input_data.email} já cadastrado")

        patient = Patient(
            id=str(uuid.uuid4()),
            name=input_data.name,
            birth_date=input_data.birth_date,
            gender=Gender(input_data.gender),
            weight_kg=input_data.weight_kg,
            height_cm=input_data.height_cm,
            email=input_data.email,
        )
        patient.validate()

        saved = self._repository.save(patient)
        return RegisterPatientOutput(patient=saved)