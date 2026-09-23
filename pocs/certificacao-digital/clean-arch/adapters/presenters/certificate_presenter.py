from typing import Optional

from entities.certificate import Certificate
from adapters.schemas.certificate_schema import CertificateResponse, VerificationResponse


class CertificatePresenter:

    @staticmethod
    def to_response(certificate: Certificate) -> CertificateResponse:
        return CertificateResponse(
            id=certificate.id,
            student_id=certificate.student_id,
            course_id=certificate.course_id,
            issuer_id=certificate.issuer_id,
            issued_at=certificate.issued_at,
            verification_hash=certificate.verification_hash,
            is_valid=certificate.is_valid,
        )

    @staticmethod
    def to_verification_response(
        is_valid: bool,
        certificate: Optional[Certificate],
    ) -> VerificationResponse:
        return VerificationResponse(
            is_valid=is_valid,
            certificate=CertificatePresenter.to_response(certificate) if certificate else None,
        )