from domain.entities.patient import Patient
from domain.exceptions import DuplicateEmailError
from ports.input.register_patient_use_case import (
    RegisterPatientCommand,
    RegisterPatientUseCasePort,
)
from ports.output.notification_service_port import NotificationServicePort
from ports.output.patient_repository_port import PatientRepositoryPort


class RegisterPatientUseCaseImpl(RegisterPatientUseCasePort):
    def __init__(
        self,
        patient_repo: PatientRepositoryPort,
        notification_service: NotificationServicePort,
    ) -> None:
        self._patient_repo = patient_repo
        self._notification_service = notification_service

    async def execute(self, command: RegisterPatientCommand) -> Patient:
        existing = await self._patient_repo.find_by_email(command.email)
        if existing:
            raise DuplicateEmailError(command.email)

        patient = Patient(
            name=command.name,
            email=command.email,
            age=command.age,
            gender=command.gender,
            health_goals=command.health_goals,
        )
        saved = await self._patient_repo.save(patient)
        await self._notification_service.send_welcome(saved)
        return saved