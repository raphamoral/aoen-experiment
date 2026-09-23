from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from adapters.output.persistence.models import PatientModel
from domain.entities.patient import Patient
from ports.output.patient_repository_port import PatientRepositoryPort


class SQLAlchemyPatientRepository(PatientRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_domain(self, model: PatientModel) -> Patient:
        return Patient(
            id=model.id,
            name=model.name,
            email=model.email,
            age=model.age,
            gender=model.gender,
            health_goals=list(model.health_goals),
            created_at=model.created_at,
        )

    def _to_model(self, patient: Patient) -> PatientModel:
        return PatientModel(
            id=patient.id,
            name=patient.name,
            email=patient.email,
            age=patient.age,
            gender=patient.gender,
            health_goals=patient.health_goals,
            created_at=patient.created_at,
        )

    async def save(self, patient: Patient) -> Patient:
        model = self._to_model(patient)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def find_by_id(self, patient_id: UUID) -> Patient | None:
        result = await self._session.execute(
            select(PatientModel).where(PatientModel.id == patient_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def find_by_email(self, email: str) -> Patient | None:
        result = await self._session.execute(
            select(PatientModel).where(PatientModel.email == email)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None