from typing import List, Optional

from sqlalchemy.orm import Session

from adapters.outbound.persistence.models import CertificateModel
from domain.entities.certificate import Certificate
from ports.outbound.certificate_repository_port import CertificateRepositoryPort


class SQLAlchemyCertificateRepository(CertificateRepositoryPort):
    """
    Driven adapter: persists and retrieves Certificate aggregates using
    SQLAlchemy.  Translates between the ORM model (infrastructure concern)
    and the domain entity (business concern) so neither layer leaks into
    the other.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, certificate: Certificate) -> None:
        model = CertificateModel(
            id=certificate.id,
            student_id=certificate.student_id,
            course_id=certificate.course_id,
            student_name=certificate.student_name,
            course_name=certificate.course_name,
            issuer_name=certificate.issuer_name,
            duration_hours=certificate.duration_hours,
            issued_at=certificate.issued_at,
            certificate_hash=certificate.certificate_hash,
            is_valid=certificate.is_valid,
            revoked_at=certificate.revoked_at,
            revocation_reason=certificate.revocation_reason,
        )
        self._session.add(model)
        self._session.commit()

    def update(self, certificate: Certificate) -> None:
        model = self._session.get(CertificateModel, certificate.id)
        if model:
            model.is_valid = certificate.is_valid
            model.revoked_at = certificate.revoked_at
            model.revocation_reason = certificate.revocation_reason
            self._session.commit()

    def find_by_id(self, certificate_id: str) -> Optional[Certificate]:
        model = self._session.get(CertificateModel, certificate_id)
        return self._to_domain(model) if model else None

    def find_by_hash(self, certificate_hash: str) -> Optional[Certificate]:
        model = (
            self._session.query(CertificateModel)
            .filter(CertificateModel.certificate_hash == certificate_hash)
            .first()
        )
        return self._to_domain(model) if model else None

    def find_by_student_id(self, student_id: str) -> List[Certificate]:
        models = (
            self._session.query(CertificateModel)
            .filter(CertificateModel.student_id == student_id)
            .order_by(CertificateModel.issued_at.desc())
            .all()
        )
        return [self._to_domain(m) for m in models]

    def find_active_by_student_and_course(
        self, student_id: str, course_id: str
    ) -> Optional[Certificate]:
        model = (
            self._session.query(CertificateModel)
            .filter(
                CertificateModel.student_id == student_id,
                CertificateModel.course_id == course_id,
                CertificateModel.is_valid == True,  # noqa: E712
            )
            .first()
        )
        return self._to_domain(model) if model else None

    # ------------------------------------------------------------------

    def _to_domain(self, model: CertificateModel) -> Certificate:
        return Certificate(
            id=model.id,
            student_id=model.student_id,
            course_id=model.course_id,
            student_name=model.student_name,
            course_name=model.course_name,
            issuer_name=model.issuer_name,
            duration_hours=model.duration_hours,
            issued_at=model.issued_at,
            certificate_hash=model.certificate_hash,
            is_valid=model.is_valid,
            revoked_at=model.revoked_at,
            revocation_reason=model.revocation_reason,
        )