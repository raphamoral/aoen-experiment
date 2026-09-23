from datetime import date
from typing import List, Optional

from sqlalchemy.orm import Session

from entities.patient import Gender, Patient
from frameworks.db.models import PatientModel
from use_cases.ports.patient_repository_port import PatientRepositoryPort


class SqlAlchemyPatientRepository(PatientRepositoryPort):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, patient: Patient) -> Patient:
        existing = self._session.query(PatientModel).filter_by(id=patient.id).first()
        if existing:
            existing.name = patient.name
            existing.birth_date = patient.birth_date.isoformat()
            existing.gender = patient.gender.value
            existing.weight_kg = patient.weight_kg
            existing.height_cm = patient.height_cm
            existing.email = patient.email
        else:
            self._session.add(
                PatientModel(
                    id=patient.id,
                    name=patient.name,
                    birth_date=patient.birth_date.isoformat(),
                    gender=patient.gender.value,
                    weight_kg=patient.weight_kg,
                    height_cm=patient.height_cm,
                    email=patient.email,
                )
            )
        self._session.commit()
        return patient

    def find_by_id(self, patient_id: str) -> Optional[Patient]:
        model = self._session.query(PatientModel).filter_by(id=patient_id).first()
        return self._to_entity(model) if model else None

    def find_by_email(self, email: str) -> Optional[Patient]:
        model = self._session.query(PatientModel).filter_by(email=email).first()
        return self._to_entity(model) if model else None

    def find_all(self) -> List[Patient]:
        return [self._to_entity(m) for m in self._session.query(PatientModel).all()]

    def delete(self, patient_id: str) -> None:
        model = self._session.query(PatientModel).filter_by(id=patient_id).first()
        if model:
            self._session.delete(model)
            self._session.commit()

    def _to_entity(self, model: PatientModel) -> Patient:
        return Patient(
            id=model.id,
            name=model.name,
            birth_date=date.fromisoformat(model.birth_date),
            gender=Gender(model.gender),
            weight_kg=model.weight_kg,
            height_cm=model.height_cm,
            email=model.email,
        )