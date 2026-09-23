from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from entities.certificate import Certificate
from frameworks.db.models import CertificateModel
from use_cases.ports.certificate_repository import CertificateRepository


class SQLAlchemyCertificateRepository(CertificateRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, certificate: Certificate) -> Certificate:
        model = CertificateModel(
            id=str(certificate.id),
            student_id=str(certificate.student_id),
            course_id=str(certificate.course_id),
            issuer_id=str(certificate.issuer_id),
            issued_at=certificate.issued_at,
            verification_hash=certificate.verification_hash,
            is_valid=certificate.is_valid,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def find_by_id(self, certificate_id: UUID) -> Optional[Certificate]:
        model = (
            self._session.query(CertificateModel)
            .filter_by(id=str(certificate_id))
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_hash(self, verification_hash: str) -> Optional[Certificate]:
        model = (
            self._session.query(CertificateModel)
            .filter_by(verification_hash=verification_hash)
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_student_id(self, student_id: UUID) -> list[Certificate]:
        models = (
            self._session.query(CertificateModel)
            .filter_by(student_id=str(student_id))
            .all()
        )
        return [self._to_entity(m) for m in models]

    def update(self, certificate: Certificate) -> Certificate:
        model = (
            self._session.query(CertificateModel)
            .filter_by(id=str(certificate.id))
            .first()
        )
        if not model:
            raise ValueError(f"Certificate '{certificate.id}' not found")
        model.is_valid = certificate.is_valid
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: CertificateModel) -> Certificate:
        # Pass verification_hash so __post_init__ skips hash regeneration
        return Certificate(
            id=UUID(model.id),
            student_id=UUID(model.student_id),
            course_id=UUID(model.course_id),
            issuer_id=UUID(model.issuer_id),
            issued_at=model.issued_at,
            verification_hash=model.verification_hash,
            is_valid=model.is_valid,
        )